from models.metrics import (pw_used_explode,
                            pw_used_penetrate,
                            pw_used_reroll,
                            pw_used_drop_highest,
                            pw_used_drop_lowest)
from functions.workhorses import dice_roll
from functions.checks import (check_value_vs_throws as check_v_v_t,
                              check_edge_vs_two as check_e_v_t,
                              check_value_for_explode as check_v_exp,
                              check_value_for_penetrate as check_v_pen,
                              check_value_vs_edge as check_v_v_e)


def postfix_magick(throws_result_list, dice_parts):
    throws = dice_parts["throws"]
    edge = dice_parts["edge"]
    postfix = dice_parts["postfix"]
    value = dice_parts["value"]
    match postfix:
        # drop lowest
        case "dl":
            check_v_v_t(throws, value)
            counter = 0
            while counter < value:
                throws_result_list.remove(min(throws_result_list))
                counter += 1
            pw_used_drop_lowest.inc()
            return throws_result_list

        # drop highest
        case "dh":
            check_v_v_t(throws, value)
            counter = 0
            while counter < value:
                throws_result_list.remove(max(throws_result_list))
                counter += 1
            pw_used_drop_highest.inc()
            return throws_result_list

        # reroll
        case "rr":
            check_v_v_e(edge, value)
            new_throws_result_list = []
            for throws_result in throws_result_list:
                if throws_result <= value:
                    additional_roll = dice_roll(1, edge)
                    new_throws_result_list += additional_roll
                else:
                    new_throws_result_list.append(throws_result)
            pw_used_reroll.inc()
            return new_throws_result_list

        # exploding dice
        case "exp":
            check_e_v_t(edge)
            if value == "" or value > edge:
                value = edge
            else:
                check_v_exp(value)
            new_throws_result_list = []

            for throw_result in throws_result_list:
                check = throw_result
                new_throws_result_list.append(throw_result)
                while check >= value:
                    additional_roll = dice_roll(1, edge)
                    new_throws_result_list += additional_roll
                    check = additional_roll[0]
            pw_used_explode.inc()
            return new_throws_result_list

        # penetrating dice
        case "pen":
            check_e_v_t(edge)
            if value == "" or value > edge:
                value = edge
            else:
                check_v_pen(value)
            new_throws_result_list = []

            for throw_result in throws_result_list:
                check = throw_result
                new_throws_result_list.append(throw_result)
                while check >= value:
                    additional_roll = dice_roll(1, edge)
                    penetrating_result = additional_roll[0] - 1
                    new_throws_result_list.append(penetrating_result)
                    check = additional_roll[0]
            pw_used_penetrate.inc()
            return new_throws_result_list

        # do nothing
        case _:
            return throws_result_list
