def test_optimize():
    """
    This function has a doc string which will be removed by two levels of
    optimization and an assert that will fail if there is no optimization.
    """
    # The assert is removed by one level of optimization
    assert False is True
    return True
