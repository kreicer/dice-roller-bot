from functions.workhorses import dice_roll
from functions.checks import (check_value_vs_throws as check_v_v_t,
                              check_edge_vs_two as check_e_v_t,
                              check_value_for_explode as check_v_exp)


def postfix_magick(throws_result_list, dice_parts):
    match dice_parts["postfix"]:
        # drop lowest
        case "dl":
            check_v_v_t(dice_parts["throws"], dice_parts["value"])
            counter = 0
            while counter < dice_parts["value"]:
                throws_result_list.remove(min(throws_result_list))
                counter += 1
            return throws_result_list

        # drop highest
        case "dh":
            check_v_v_t(dice_parts["throws"], dice_parts["value"])
            counter = 0
            while counter < dice_parts["value"]:
                throws_result_list.remove(max(throws_result_list))
                counter += 1
            return throws_result_list

        # exploding dice
        case "exp":
            dice_edge = dice_parts["edge"]
            check_e_v_t(dice_edge)
            dice_value = dice_parts["value"]
            if dice_value == "max" or dice_value > dice_edge:
                dice_value = dice_edge
            else:
                check_v_exp(dice_value)
            new_throws_result_list = []

            for throw_result in throws_result_list:
                check = throw_result
                new_throws_result_list.append(throw_result)
                while check >= dice_value:
                    additional_roll = dice_roll(1, dice_edge)
                    new_throws_result_list += additional_roll
                    check = additional_roll[0]
            return new_throws_result_list

        # do nothing
        case _:
            return throws_result_list
