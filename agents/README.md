
**AGENTS**
These agents are designed for various experimental conditions. They can be modified to suit the desired experimental manipulation.

These agents are loaded based on the password input by the user in the login. These are explicitly listed in the add_passwords.py.

**Temperature optimization** 
The Wordgame pre-prompt (system message) is provided in the context of the AI as the guesser and the user as the giver.
The temperature is manipulated and labelled in the file name.
- temp0, temp0_2, temp 0_4, temp 0_7, temp1, temp_1_2, temp1_4, temp1_7, temp2

**Temperature conditions**
AI=Guesser, User=Giver
1_TEMP_high, 1_TEMP_low, 1_TEMP_mid

AI=Giver, User=Guesser
2_TEMP_high, 2_TEMP_low, 2_TEMP_mid

**Prompt conditions**
AI=Guesser, User=Giver
1_PROMPT_high, 1_PROMPT_low

AI=Giver, User=Guesser
2_PROMPT_high, 2_PROMPT_low