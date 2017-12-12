"""WSGI app."""

from enum import Enum
from subprocess import CalledProcessError, check_output
from urllib.parse import unquote

from flask import request
from peewee import DoesNotExist
from pyxb import PyXBException

from filedb import FileError
from homeinfo.crm import Customer
from wsgilib import OK, Error, XML, Binary, Application
from openimmo import factories, openimmo
from openimmodb import Immobilie, Anhang

from immosearch.errors import NoSuchCustomer, InvalidOptionsCount, \
    NotAnInteger, InvalidParameterError, UserNotAllowed, AttachmentNotFound
from immosearch.filter import RealEstateSieve
from immosearch.orm import Blacklist
from immosearch.pager import Pager
from immosearch.selector import RealEstateDataSelector
from immosearch.sort import RealEstateSorter

__all__ = ['APPLICATION']


APPLICATION = Application('ImmoSearch', cors=True, debug=True)


class Separators(Enum):
    """Special separation characters."""

    QUERY = '&'
    ASS = '='
    OPTION = ','
    ATTR = ':'
    PATH = '/'


class Operations(Enum):
    """Valid query operations."""

    FILTER = 'filter'
    INCLUDE = 'include'
    SORT = 'sort'
    PAGING = 'paging'
    NOCACHE = 'nocache'


class PathNodes(Enum):
    """Valid path nodes."""

    OPENIMMO = 'openimmo'
    CUSTOMER = 'customer'


def _get_includes(value):
    """Select options."""

    for include in value.split(Separators.OPTION.value):
        yield include


def _get_sorting(value):
    """Generate sorting data."""

    for sort_option in value.split(Separators.OPTION.value):
        try:
            key, mode = sort_option.split(Separators.ATTR.value)
        except ValueError:
            key = sort_option
            desc = False
        else:
            desc = mode == 'desc'

        yield (key, desc)


def _get_paging(value):
    """Generate scaling data."""

    paging_opts = value.split(Separators.OPTION.value)

    if len(paging_opts) != 2:
        raise InvalidOptionsCount() from None

    limit = None
    page = None

    for paging_opt in paging_opts:
        option, *values = paging_opt.split(Separators.ATTR.value)
        value = Separators.ATTR.value.join(values)

        if option == 'limit':
            try:
                limit = int(value)
            except (ValueError, TypeError):
                raise NotAnInteger(value) from None
        elif option == 'page':
            try:
                page = int(value)
            except (ValueError, TypeError):
                raise NotAnInteger(value) from None
        else:
            raise InvalidParameterError(option) from None

    if limit is None or page is None:
        return None

    return (limit, page)


def _get_real_estates(customer):
    """Returns real estates for the respective customer."""

    for real_estate in Immobilie.by_customer(customer):
        yield (real_estate, real_estate.to_dom())


def _filter_real_estates(real_estates, filters, sort, paging, includes):
    """Perform sieving, sorting and rendering."""

    if filters is not None:
        real_estates = RealEstateSieve(real_estates, filters)

    real_estates = RealEstateDataSelector(real_estates, selections=includes)

    if sort is not None:
        real_estates = RealEstateSorter(real_estates, sort)

    if paging is not None:
        page_size, page_num = paging
        real_estates = Pager(real_estates, limit=page_size, page=page_num)

    return real_estates


def _set_paging(anbieter, paging):
    """Sets paging information."""

    if paging is not None:
        page_size, page_num = paging
        anbieter.user_defined_simplefield.append(
            openimmo.user_defined_simplefield(page_size, feldname='page_size'))
        anbieter.user_defined_simplefield.append(
            openimmo.user_defined_simplefield(page_num, feldname='page_num'))


def _set_fortune(anbieter):
    """Sets a random message of the day (easter egg)."""

    try:
        fortune = check_output('/usr/games/fortune').decode().strip()
    except (FileNotFoundError, CalledProcessError, ValueError):
        pass
    else:
        anbieter.user_defined_simplefield.append(
            openimmo.user_defined_simplefield(fortune, feldname='motd'))


def _gen_anbieter(customer, paging):
    """Generates an openimmo.anbieter DOM."""

    anbieter = factories.anbieter(
        str(customer.id), customer.name, str(customer.id))
    _set_paging(anbieter, paging)
    _set_fortune(anbieter)
    return anbieter


def _get_attachment(aid):
    """REturns the respective attachment."""

    try:
        return Anhang.get(Anhang.id == aid)
    except DoesNotExist:
        raise AttachmentNotFound()


def _get_options():
    """Parses the query dictionary for options."""

    filters = None
    sort = None
    paging = None
    includes = None

    for key, value in request.args.items():
        try:
            value = unquote(value)
        except TypeError:
            value = None

        if key == Operations.INCLUDE.value:
            includes = tuple(_get_includes(value))
        elif key == Operations.FILTER.value:
            filters = value
        elif key == Operations.SORT.value:
            sort = tuple(_get_sorting(value))
        elif key == Operations.PAGING.value:
            paging = _get_paging(value)

    return (filters, sort, paging, includes)


def _get_customer(cid):
    """Returns the respective customer."""

    try:
        return Customer.get(Customer.id == cid)
    except DoesNotExist:
        raise NoSuchCustomer(cid)


def _set_validated_real_estates(anbieter, real_estates):
    """Sets validated real estates."""
    flawed = openimmo.user_defined_extend()
    count = 0

    for count, (_, dom) in enumerate(real_estates, start=1):
        try:
            dom.toxml()
        except PyXBException as error:
            feld = openimmo.feld(
                name='Flawed real estate', wert=dom.objektnr_extern)
            feld.typ.append(str(error))
            flawed.feld.append(feld)
        else:
            anbieter.immobilie.append(dom)

    if flawed.feld:
        anbieter.user_defined_extend.append(flawed)

    anbieter.user_defined_simplefield.append(
        openimmo.user_defined_simplefield(count, feldname='count'))
    return anbieter


@APPLICATION.route('/attachment/<int:aid>', strict_slashes=False)
def get_attachment(aid):
    """Returns the respective attachment."""

    print('SHA256:', request.args.get('sha256sum'), flush=True)

    if request.args.get('sha256sum', False):
        try:
            return OK(_get_attachment(aid).sha256sum)
        except FileError:
            raise Error('Could not get file checksum.', status=500)

    try:
        return Binary(_get_attachment(aid).data)
    except FileError:
        raise Error('Could not find file for attachment.', status=500)



@APPLICATION.route('/customer/<int:cid>', strict_slashes=False)
def get_customer(cid):
    """Returns the respective customer's real estates."""

    filters, sort, paging, includes = _get_options()
    customer = _get_customer(cid)

    try:
        Blacklist.get(Blacklist.customer == customer)
    except DoesNotExist:
        real_estates = _filter_real_estates(
            _get_real_estates(customer), filters, sort, paging, includes)
        anbieter = _gen_anbieter(customer, paging)
        return XML(_set_validated_real_estates(anbieter, real_estates))

    return UserNotAllowed(cid)
