missing_permissions = f"<red>Missing Permissions<end>\n" \
                      f"Sorry, but you need administrator permissions to manage options for this server."
bot_missing_permissions = f"<red>Bot Missing Permissions<end>\n" \
                          f"Dice Roller have missing permissions to answer you in this channel. " \
                          f"You can solve it by adding rights in channel or server management section."
shortcut_many_arguments = "<red>Shortcuts Limit Reached<end>\n" \
                          "{0}"
bad_argument = "<red>Bad Argument<end>\n" \
               "{0}"
wrong_dice_error = "Wrong dice or modifier.\n" \
                   "Dice pattern is <blue>[throws]d[edge]/[postfix]:[value]<end>.\n" \
                   "Fate/Fudge dice pattern is <blue>[throws]dF<end>.\n"\
                   "Modifier should start from <blue>+<end> or <blue>-<end> and can be another dice or number."
wrong_sign_error = "Dice modifiers can be additive <blue>+<end> or subtractive <blue>-<end> only."
zero_throws_error = "Number of dice throws can not be zero."
throws_limit_error = "Number of throws <blue>{0}<end> is greater than the current limit of <blue>{1}<end>."
zero_mod_error = "Modifier can not be zero."
mod_limit_error = "Modifier <blue>{0}<end> is greater than the current limit of <blue>{1}<end>."
zero_edge_error = "Value of dice edge can not be zero or empty."
edge_limit_error = "Dice edge value <blue>{0}<end> is greater than the current limit of <blue>{1}<end>."
empty_postfix_error = "Alias to postfix can not be empty."
bad_postfix_error = "Can not find this alias to existing postfix. " \
                    "You can list all available postfixes with:\n<blue>/postfix<end>"
value_vs_throws_error = "Value can not be higher or equal to number of throws in this postfix."
value_vs_edge_error = "Value can not be higher than dice edge in this postfix."
edge_vs_two_error = "Can not use this postfix with dice edge equal to 1."
infinity_loop_error = "This dice can not be rolled with value equal to 1 - protection from infinity loop."
value_for_multiply_error = "Multiplier value (with other dice) cannot be higher than group limit <blue>{0}<end>."
postfix_right_error = "Can not find this short name to existing postfix. " \
                      "You can list all available postfixes with:\n<blue>/postfix<end>"
shortcut_name_error = "Shortcut name can contain only letters and numbers."

argument_parsing_error = "<red>Argument Parsing Error<end>\n" \
                         "{0}"
throws_groups_error_text = "Number of throw groups <blue>{0}<end> is greater than the current limit of <blue>{1}<end>."
bucket_error = "Number of elements of the dice <blue>{0}<end> is greater than the current limit of <blue>{1}<end>."

missing_required_argument = "<red>Missing Required Argument<end>\n" \
                            "You should to specify one valid dice at least. " \
                            "Try something like:\n<blue>{0}roll 4d20/dl:1+3<end>"

shortcut_limit_error = "Looks like you reach limit of shortcuts for this server. Delete or overwrite the old one."

sql_operational_error = "<red>SQL Operational Error<end>\n" \
                        "Looks like Admin Database currently unavailable.\n" \
                        "Please, report to developer - {0}."
