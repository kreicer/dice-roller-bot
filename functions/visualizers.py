from table2ascii import table2ascii as t2a, Alignment, PresetStyle, Merge


def convert_dice_for_output(roll, limit):
    if len(roll) >= limit:
        roll = roll[:limit-3] + "..."
    return roll


def body_for_output(rolls_list, result):
    delimiter = " "
    rolls_output = ""
    output_count = 0
    total_len = 37
    result_len = len(str(result))
    rolls_len = total_len - result_len - 2
    for roll in rolls_list:
        roll_len = len(str(roll))
        if output_count + roll_len == rolls_len:
            rolls_output += str(roll) + "\n"
            output_count = 0
        elif output_count + roll_len < rolls_len:
            rolls_output += str(roll) + delimiter
            output_count += roll_len + 1
        else:
            rolls_output += "\n" + str(roll) + delimiter
            output_count = roll_len + 1
    result_output = '[' + str(result) + ']'
    result_column = result_len + 4
    rolls_output_len = len(rolls_output)
    if rolls_output_len < 8:
        rolls_output_len = 8
    if rolls_output_len < rolls_len:
        rolls_column = rolls_output_len + 2
    else:
        rolls_column = rolls_len + 2
    return rolls_output, result_output, rolls_column, result_column


def create_table(table_header, rolls_string, sum_string, rolls_column, result_column):
    body_header = ["rolls", "sum"]
    table_body = [rolls_string, sum_string]
    output = t2a(
        header=[table_header, Merge.LEFT],
        body=[body_header, table_body],
        alignments=[Alignment.CENTER, Alignment.CENTER],
        column_widths=[rolls_column, result_column],
        style=PresetStyle.double_thin_box
    )
    return output


def create_row(dice_id, dice_rolls, dice_sum):
    dice_id = "(" + str(dice_id) + ")"
    dice_sum = "[" + str(dice_sum) + "]"
    row = [dice_id, dice_rolls, dice_sum]
    return row


def new_create_table(rolls_string, sum_string, rolls_column, result_column):
    table_header = ["dice", "rolls", "sum"]
    table_body = [rolls_string, sum_string]
    output = t2a(
        header=[table_header, Merge.LEFT],
        body=[table_body],
        alignments=[Alignment.CENTER, Alignment.CENTER],
        column_widths=[rolls_column, result_column],
        style=PresetStyle.double_thin_box
    )
    return output


def make_subzero(not_subzero):
    subzero = []
    for list_object in not_subzero:
        list_object = "-" + str(list_object)
        subzero.append(list_object)
    return subzero


def fate_subzero(not_subzero):
    subzero = []
    for list_object in not_subzero:
        if list_object == "+":
            list_object = "-"
        elif list_object == "-":
            list_object = "+"
        else:
            list_object = "."
        subzero.append(list_object)
    return subzero


# make dice label for table from args
def dice_maker(*args):
    args_list = list(args)
    result = ''
    for arg in args_list:
        result += str(arg)
    if result.endswith("d/:"):
        result = result[:-3]
    if result.endswith("/:"):
        result = result[:-2]
    if result.endswith(":"):
        result = result[:-1]
    return result
