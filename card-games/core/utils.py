def partition(lst, condition):
    true_list = [x for x in lst if condition(x)]
    false_list = [x for x in lst if not condition(x)]
    return true_list, false_list