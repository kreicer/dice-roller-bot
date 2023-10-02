from models.metrics import postfix_counter
from functions.workhorses import dice_roll
from functions.checks import (check_value_vs_throws,
                              check_edge_vs_two as check_e_v_t,
                              check_value_vs_edge as check_v_v_e,
                              check_value_for_multiply as check_v_f_mul, check_value_for_infinity_loop)


def postfix_check(dice_parts):
    throws = dice_parts["throws"]
    edge = dice_parts["edge"]
    postfix = dice_parts["postfix"]
    value = dice_parts["value"]
    match postfix:
        # drop lowest | drop highest | keep lowest | keep highest
        case "dl" | "dh" | "kl" | "kh":
            check_value_vs_throws(throws, value)
        # reroll
        case "rr":
            check_v_v_e(edge, value)
        # exploding dice | penetrating dice
        case "exp" | "pen":
            check_e_v_t(edge)
            if value != "" or value < edge:
                check_value_for_infinity_loop(value)
        # multiplier
        case "x":
            check_v_f_mul(throws, value)
        # do nothing
        case _:
            pass


def postfix_magick(throws_result_list, dice_parts):
    throws = dice_parts["throws"]
    edge = dice_parts["edge"]
    postfix = dice_parts["postfix"]
    value = dice_parts["value"]
    match postfix:
        # drop lowest
        case "dl":
            counter = 0
            while counter < value:
                throws_result_list.remove(min(throws_result_list))
                counter += 1
            postfix_counter.labels("drop_lowest")
            postfix_counter.labels("drop_lowest").inc()
            return throws_result_list

        # drop highest
        case "dh":
            counter = 0
            while counter < value:
                throws_result_list.remove(max(throws_result_list))
                counter += 1
            postfix_counter.labels("drop_highest")
            postfix_counter.labels("drop_highest").inc()
            return throws_result_list

        # reroll
        case "rr":
            new_throws_result_list = []
            for throws_result in throws_result_list:
                if throws_result <= value:
                    additional_roll = dice_roll(1, edge)
                    new_throws_result_list += additional_roll
                else:
                    new_throws_result_list.append(throws_result)
            postfix_counter.labels("reroll")
            postfix_counter.labels("reroll").inc()
            return new_throws_result_list

        # exploding dice
        case "exp":
            if value == "" or value > edge:
                value = edge
            new_throws_result_list = []

            for throw_result in throws_result_list:
                check = throw_result
                new_throws_result_list.append(throw_result)
                while check >= value:
                    additional_roll = dice_roll(1, edge)
                    new_throws_result_list += additional_roll
                    check = additional_roll[0]
            postfix_counter.labels("explode")
            postfix_counter.labels("explode").inc()
            return new_throws_result_list

        # penetrating dice
        case "pen":
            if value == "" or value > edge:
                value = edge
            new_throws_result_list = []

            for throw_result in throws_result_list:
                check = throw_result
                new_throws_result_list.append(throw_result)
                while check >= value:
                    additional_roll = dice_roll(1, edge)
                    penetrating_result = additional_roll[0] - 1
                    new_throws_result_list.append(penetrating_result)
                    check = additional_roll[0]
            postfix_counter.labels("penetrate")
            postfix_counter.labels("penetrate").inc()
            return new_throws_result_list

        # keep lowest
        case "kl":
            new_throws_result_list = []
            counter = 0
            while counter < value:
                new_throws_result_list.append(min(throws_result_list))
                throws_result_list.remove(min(throws_result_list))
                counter += 1
            postfix_counter.labels("keep_lowest")
            postfix_counter.labels("keep_lowest").inc()
            return new_throws_result_list

        # keep highest
        case "kh":
            new_throws_result_list = []
            counter = 0
            while counter < value:
                new_throws_result_list.append(max(throws_result_list))
                throws_result_list.remove(max(throws_result_list))
                counter += 1
            postfix_counter.labels("keep_highest")
            postfix_counter.labels("keep_highest").inc()
            return new_throws_result_list

        case "x":
            counter = (throws * value) - throws
            while counter:
                additional_roll = dice_roll(1, edge)
                throws_result_list += additional_roll
                counter -= 1
            postfix_counter.labels("multiplier")
            postfix_counter.labels("multiplier").inc()
            return throws_result_list

        # do nothing
        case _:
            return throws_result_list
