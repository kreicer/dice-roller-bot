import decimal

from lang.EN.errors import postfix_limit_error
from models.limits import modifier_limit
from models.metrics import postfix_counter
from functions.workhorses import dice_roll, calc_result
from functions.checks import (check_value_vs_throws,
                              check_edge_vs_two as check_e_v_t,
                              check_value_vs_edge as check_v_v_e,
                              check_value_for_infinity_loop, check_ten, check_limit)


def postfix_check(dice_parts):
    throws = dice_parts["throws"]
    edge = dice_parts["edge"]
    postfix = dice_parts["postfix"]
    value = dice_parts["value"]
    match postfix:
        # drop lowest | drop highest | keep lowest | keep highest
        case "dl" | "dh" | "kl" | "kh":
            check_value_vs_throws(throws, value)
        # re-roll | minimum | divisor | target | hit-n-miss | lucky | cursed
        case "rr" | "min" | "div" | "trg" | "hit" | "luc" | "cur":
            check_v_v_e(edge, value)
        # additive | subtraction
        case "add" | "sub":
            error_text = postfix_limit_error.format(value, modifier_limit)
            check_limit(value, modifier_limit, error_text)
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
        # chronicles of darkness system | world of darkness system
        case "cod" | "wod" as cc:
            check_ten(edge)
            if value != "":
                check_v_v_e(edge, value)
            if cc == "cod":
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
            counter = 0
            if value == "":
                value = edge
            for throw_result in throws_result_list:
                check = throw_result
                new_list.append(throw_result)
                while check >= value:
                    additional_roll = dice_roll(1, edge)
                    new_list += additional_roll
                    check = additional_roll[0]
                    counter += 1
                    if counter > 50:
                        break
            sub_sum = calc_result(new_list)

            # metrics
            postfix_counter.labels("explode")
            postfix_counter.labels("explode").inc()

        # penetrating dice
        case "pen":
            counter = 0
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
                    counter += 1
                    if counter > 50:
                        break
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

        # target
        case "trg":
            counter = 0
            new_list = throws_result_list
            for result in new_list:
                if result <= value:
                    counter += 1
            sub_sum = counter

            # metrics
            postfix_counter.labels("target")
            postfix_counter.labels("target").inc()

        # hit-n-miss
        case "hit":
            counter = 0
            miss = 0
            new_list = throws_result_list
            for result in new_list:
                if result <= value:
                    counter += 1
                else:
                    miss += result - value
            miss = decimal.Decimal("0." + str(miss))
            sub_sum = counter + miss

            # metrics
            postfix_counter.labels("hit-n-miss")
            postfix_counter.labels("hit-n-miss").inc()

        # divisor
        case "div":
            for throws_result in throws_result_list:
                new_list.append(-(-throws_result // value))
            sub_sum = calc_result(new_list)

            # metrics
            postfix_counter.labels("divisor")
            postfix_counter.labels("divisor").inc()

        # multiplier
        case "mul":
            for throws_result in throws_result_list:
                new_list.append(throws_result * value)
            sub_sum = calc_result(new_list)

            # metrics
            postfix_counter.labels("multiplier")
            postfix_counter.labels("multiplier").inc()

        # additive
        case "add":
            for throws_result in throws_result_list:
                new_list.append(throws_result + value)
            sub_sum = calc_result(new_list)

            # metrics
            postfix_counter.labels("additive")
            postfix_counter.labels("additive").inc()

        # subtraction
        case "sub":
            for throws_result in throws_result_list:
                new_list.append(throws_result - value)
            sub_sum = calc_result(new_list)

            # metrics
            postfix_counter.labels("subtraction")
            postfix_counter.labels("subtraction").inc()

        # chronicles of darkness
        case "cod":
            check_number = 0
            if value == "":
                value = edge
            for throw_result in throws_result_list:
                check = throw_result
                new_list.append(throw_result)
                while check >= value:
                    additional_roll = dice_roll(1, edge)
                    new_list += additional_roll
                    check = additional_roll[0]
                    check_number += 1
                    if check_number > 50:
                        break
            counter = 0
            for result in new_list:
                if result >= 8:
                    counter += 1
            sub_sum = counter
            # metrics
            postfix_counter.labels("cod")
            postfix_counter.labels("cod").inc()

        # world of darkness
        case "wod":
            for throw_result in throws_result_list:
                check = throw_result
                new_list.append(throw_result)
                while check == 10:
                    additional_roll = dice_roll(1, edge)
                    new_list += additional_roll
                    check = additional_roll[0]
            counter = 0
            for result in new_list:
                if result >= value:
                    counter += 1
                if result == 1:
                    counter -= 1
            sub_sum = counter
            # metrics
            postfix_counter.labels("wod")
            postfix_counter.labels("wod").inc()

        # lucky
        case "luc":
            for throws_result in throws_result_list:
                if throws_result <= value:
                    new_throws_result = edge
                    new_list.append(new_throws_result)
                else:
                    new_list.append(throws_result)
            sub_sum = calc_result(new_list)

            # metrics
            postfix_counter.labels("lucky")
            postfix_counter.labels("lucky").inc()

        # cursed
        case "cur":
            for throws_result in throws_result_list:
                if throws_result > edge - value:
                    new_throws_result = 1
                    new_list.append(new_throws_result)
                else:
                    new_list.append(throws_result)
            sub_sum = calc_result(new_list)

            # metrics
            postfix_counter.labels("lucky")
            postfix_counter.labels("lucky").inc()

        # do nothing
        case _:
            new_list = throws_result_list
            sub_sum = calc_result(new_list)
    return new_list, sub_sum
