# Example of what users.json contains.

users = { # A list of all users.
    "8762349134109743": { # Sorted by discord_id.
        "server-nickname": "Eric Roy", # Takes eric.roy and capitalizes de name. Only available when mail is verified.

        "upc-mail-valid": "eric.roy@estudiantat.upc.edu", 
            #Blank if no valid mail, expired or pending.
        "upc-mail-pending": "",
        "mail-status": 5,
            # MAILS STATUS:
                # 0- None
                # 1- Mail entered, waiting for user tick.
                # 2- User refused mail verification, waiting for another mail.
                # 3- Verification code sended, waiting for code.
                # 4- Wrong code, waiting for code or another mail.
                # 5- Correct code, standard case scenario.
                # 6- Mail is linked now with another account.
                # 7- Changing mail (like status 1)
                # 8- Changing mail (like status 3)
                # 9- Changing mail (like status 4)
        
        "verifiaction-code": 899273,

        "subjects-selected": [ # If the user selects more than 6 subjects, here you will see all of them.
            11,
            12,
            13,
            14,
            15
        ],

        "quadrimesters": [
            1
        ],
        "subjects-added": [ # And here the selection that the bot has made.
            11,
            12,
            13,
            14,
            15
        ]
    },

    "091237819246524378": {
        # Another user...
    }
}

temp_vc = [
    { "channel-type": 3984723498723 } #For every extra channel ceated
]