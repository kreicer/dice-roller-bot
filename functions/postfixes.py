from models.metrics import postfix_counter
from functions.workhorses import dice_roll, calc_result
from functions.checks import (check_value_vs_throws,
                              check_edge_vs_two as check_e_v_t,
                              check_value_vs_edge as check_v_v_e,
                              check_value_for_infinity_loop, check_multiply)


def postfix_check(dice_parts):
    throws = dice_parts["throws"]
    edge = dice_parts["edge"]
    postfix = dice_parts["postfix"]
    value = dice_parts["value"]
    match postfix:
        # drop lowest | drop highest | keep lowest | keep highest
        case "dl" | "dh" | "kl" | "kh":
            check_value_vs_throws(throws, value)
        # reroll | minimum | divisor
        case "rr" | "min" | "div":
            check_v_v_e(edge, value)
        # counter | success
        case "c" | "suc":
            if value != "":
                check_v_v_e(edge, value)
        # exploding dice | penetrating dice
        case "exp" | "pen":
            check_e_v_t(edge)
            if value != "":
                check_v_v_e(edge, value)
                check_value_for_infinity_loop(value)
        # all other
        case _:
            pass


def postfix_magick(throws_result_list, dice_parts):
    edge = dice_parts["edge"]
    postfix = dice_parts["postfix"]
    value = dice_parts["value"]
    new_list = []
    match postfix:

        # drop lowest
        case "dl":
            counter = 0
            while counter < value:
                throws_result_list.remove(min(throws_result_list))
                counter += 1
            new_list = throws_result_list
            sub_sum = calc_result(new_list)

            # metrics
            postfix_counter.labels("drop_lowest")
            postfix_counter.labels("drop_lowest").inc()

        # drop highest
        case "dh":
            counter = 0
            while counter < value:
                throws_result_list.remove(max(throws_result_list))
                counter += 1
            new_list = throws_result_list
            sub_sum = calc_result(new_list)

            # metrics
            postfix_counter.labels("drop_highest")
            postfix_counter.labels("drop_highest").inc()

        # reroll
        case "rr":
            for throws_result in throws_result_list:
                if throws_result <= value:
                    additional_roll = dice_roll(1, edge)
                    new_list += additional_roll
                else:
                    new_list.append(throws_result)
            sub_sum = calc_result(new_list)

            # metrics
            postfix_counter.labels("reroll")
            postfix_counter.labels("reroll").inc()

        # exploding dice
        case "exp":
            if value == "":
                value = edge
            for throw_result in throws_result_list:
                check = throw_result
                new_list.append(throw_result)
                while check >= value:
                    additional_roll = dice_roll(1, edge)
                    new_list += additional_roll
                    check = additional_roll[0]
            sub_sum = calc_result(new_list)

            # metrics
            postfix_counter.labels("explode")
            postfix_counter.labels("explode").inc()

        # penetrating dice
        case "pen":
            if value == "":
                value = edge
            for throw_result in throws_result_list:
                check = throw_result
                new_list.append(throw_result)
                while check >= value:
                    additional_roll = dice_roll(1, edge)
                    penetrating_result = additional_roll[0] - 1
                    new_list.append(penetrating_result)
                    check = additional_roll[0]
            sub_sum = calc_result(new_list)

            # metrics
            postfix_counter.labels("penetrate")
            postfix_counter.labels("penetrate").inc()

        # keep lowest
        case "kl":
            counter = 0
            while counter < value:
                new_list.append(min(throws_result_list))
                throws_result_list.remove(min(throws_result_list))
                counter += 1
            sub_sum = calc_result(new_list)

            # metrics
            postfix_counter.labels("keep_lowest")
            postfix_counter.labels("keep_lowest").inc()

        # keep highest
        case "kh":
            counter = 0
            while counter < value:
                new_list.append(max(throws_result_list))
                throws_result_list.remove(max(throws_result_list))
                counter += 1
            sub_sum = calc_result(new_list)

            # metrics
            postfix_counter.labels("keep_highest")
            postfix_counter.labels("keep_highest").inc()

        # minimum
        case "min":
            for throws_result in throws_result_list:
                if throws_result < value:
                    new_throws_result = value
                    new_list.append(new_throws_result)
                else:
                    new_list.append(throws_result)
            sub_sum = calc_result(new_list)

            # metrics
            postfix_counter.labels("minimum")
            postfix_counter.labels("minimum").inc()

        # counter
        case "c":
            if value == "":
                value = edge
            counter = 0
            new_list = throws_result_list
            for result in new_list:
                if result >= value:
                    counter += 1
            sub_sum = counter

            # metrics
            postfix_counter.labels("counter")
            postfix_counter.labels("counter").inc()

        # success
        case "suc":
            if value == "":
                value = edge
            counter = 0
            new_list = throws_result_list
            for result in new_list:
                if result >= value:
                    counter += 1
                if result == 1:
                    counter -= 1
            sub_sum = counter

            # metrics
            postfix_counter.labels("success")
            postfix_counter.labels("success").inc()

        # divisor
        case "div":
            for throws_result in throws_result_list:
                new_list.append(-(-throws_result // value))
            sub_sum = calc_result(new_list)

            # metrics
            postfix_counter.labels("divisor")
            postfix_counter.labels("divisor").inc()

        # do nothing
        case _:
            new_list = throws_result_list
            sub_sum = calc_result(new_list)
    return new_list, sub_sum
