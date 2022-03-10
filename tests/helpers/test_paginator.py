from external_offers.services.calls_history.helpers import PageItem, Paginator


def test_paginator__get_page_items__first_is_active():
    # arrange
    paginator = Paginator(
        url='http://example.com',
        current_page_number=1,
        total_count=20,
        page_size=10,
    )

    # act
    page_items = paginator.get_page_items()

    # assert
    assert len(page_items) == 3
    assert page_items[0].link == 'http://example.com?page=1'
    assert page_items[0].text == '1'
    assert page_items[0].is_active
    assert page_items[-1].link == 'http://example.com?page=2'
    assert page_items[-1].text == 'Следующая'
    assert not page_items[-1].is_active


def test_paginator__get_page_items__one_page():
    # arrange
    paginator = Paginator(
        url='http://example.com',
        current_page_number=1,
        total_count=5,
        page_size=10,
    )

    # act
    page_items = paginator.get_page_items()

    # assert
    assert not len(page_items)


def test_paginator__get_page_items__last_is_active():
    # arrange
    paginator = Paginator(
        url='http://example.com',
        current_page_number=2,
        total_count=20,
        page_size=10,
    )

    # act
    page_items = paginator.get_page_items()

    # assert
    assert len(page_items) == 3
    assert page_items[0].link == 'http://example.com?page=1'
    assert page_items[0].text == 'Предыдущая'
    assert not page_items[0].is_active
    assert page_items[-1].link == 'http://example.com?page=2'
    assert page_items[-1].text == '2'
    assert page_items[-1].is_active
