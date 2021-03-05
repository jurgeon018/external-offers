from external_offers.utils import iterate_over_list_by_chunks


def test_iterate_over_list_by_chunks__called_with_list_exceeding_limit__returns_two_chunks():
    # arrange
    test_list = [1, 2]

    # act
    chunks = list(iterate_over_list_by_chunks(
        iterable=test_list,
        chunk_size=1
    ))

    # assert
    assert chunks == [[1], [2]]
