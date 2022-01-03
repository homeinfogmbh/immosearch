"""WSGI app."""

from enum import Enum
from urllib.parse import unquote

from flask import request
from pyxb import PyXBException

from mdb import Customer
from openimmo import anbieter
from openimmo import CTD_ANON_67 as feld
from openimmo import user_defined_extend
from openimmo import user_defined_simplefield
from openimmodb import Immobilie, Anhang
from wsgilib import OK, XML, Binary, Application

from immosearch.errors import NoSuchCustomer
from immosearch.errors import InvalidOptionsCount
from immosearch.errors import NotAnInteger
from immosearch.errors import InvalidParameterError
from immosearch.errors import UserNotAllowed
from immosearch.errors import AttachmentNotFound
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


def _set_paging(anbieter, paging):  # pylint: disable=W0621
    """Sets paging information."""

    if paging is not None:
        page_size, page_num = paging
        anbieter.user_defined_simplefield.append(
            user_defined_simplefield(page_size, feldname='page_size'))
        anbieter.user_defined_simplefield.append(
            user_defined_simplefield(page_num, feldname='page_num'))


def _gen_anbieter(customer, paging):
    """Generates an openimmo.anbieter DOM."""

    result = anbieter(
        anbieternr=repr(customer), firma=str(customer),
        openimmo_anid=repr(customer))
    _set_paging(result, paging)
    return result


def _get_attachment(ident):
    """REturns the respective attachment."""

    try:
        return Anhang.get(Anhang.id == ident)
    except Anhang.DoesNotExist:
        raise AttachmentNotFound() from None


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
        return Customer.select(cascade=True).where(Customer.id == cid).get()
    except Customer.DoesNotExist:
        raise NoSuchCustomer(cid) from None


def _set_validated_real_estates(
        anbieter, real_estates):    # pylint: disable=W0621
    """Sets validated real estates."""
    flawed = user_defined_extend()
    count = 0

    for count, (_, dom) in enumerate(real_estates, start=1):
        try:
            dom.toxml()
        except PyXBException as error:
            value = str(dom.verwaltung_techn.objektnr_extern)
            feld_ = feld(name='Flawed real estate', wert=value)
            feld_.typ.append(str(error))
            flawed.feld.append(feld_)
        else:
            anbieter.immobilie.append(dom)

    if flawed.feld:
        anbieter.user_defined_extend.append(flawed)

    anbieter.user_defined_simplefield.append(
        user_defined_simplefield(count, feldname='count'))
    return anbieter


@APPLICATION.route('/attachment/<int:ident>', strict_slashes=False)
def get_attachment(ident):
    """Returns the respective attachment."""

    try:
        request.args['sha256sum']
    except KeyError:
        return Binary(_get_attachment(ident).bytes)

    return OK(_get_attachment(ident).metadata.sha256sum)


@APPLICATION.route('/customer/<int:cid>', strict_slashes=False)
def get_customer(cid):
    """Returns the respective customer's real estates."""

    filters, sort, paging, includes = _get_options()
    customer = _get_customer(cid)

    try:
        Blacklist.get(Blacklist.customer == customer)
    except Blacklist.DoesNotExist:
        real_estates = _filter_real_estates(
            _get_real_estates(customer), filters, sort, paging, includes)
        anbieter = _gen_anbieter(customer, paging)  # pylint: disable=W0621
        return XML(_set_validated_real_estates(anbieter, real_estates))

    return UserNotAllowed(cid)
