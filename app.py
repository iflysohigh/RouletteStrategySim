from flask import Flask, request, jsonify
from flask_cors import CORS
import random

app = Flask(__name__)
CORS(app)

def simulate_roulette(roulette_type, bet_amount, num_rolls, sets_of_12):
    results = []
    if roulette_type == "American":
        slots = list(range(1, 37)) + [0, '00']
    else:  # European
        slots = list(range(1, 37)) + [0]

    bets = [bet_amount, bet_amount]
    total_revenue = 0

    for r_num in range(num_rolls):
        round_result = -1 * bets[0] - bets[1]  # The initial result is losing both
        old_bets = bets[:]  # We use this as a temporary copy of the initial bets for this round

        roll = random.randint(slots)
        if isinstance(roll, str):
            roll = 0 if roll == "00" else 37  # Handling 00 as 0 and keeping unique identifier for 0

        win = False
        if roll != 0:
            if '1st12' in sets_of_12 and 1 <= roll <= 12:
                win = True
                round_result += bets[0] * 2
                bets[0] = bet_amount  # Resetting the bet amount if we win; we know this must be the first bet index if it's in the set
                bets[1] *= 2

            if '2nd12' in sets_of_12 and 13 <= roll <= 24:
                win = True
                if '1st12' in sets_of_12: 
                    round_result += bets[1] * 2  # Then we know this must be the second value
                    bets[1] = bet_amount
                    bets[0] *= 2
                else: 
                    round_result += bets[0] * 2  # Else, this must be the first value
                    bets[0] = bet_amount
                    bets[1] *= 2

            if '3rd12' in sets_of_12 and 25 <= roll <= 36:
                win = True
                round_result += bets[1] * 2  # This must be the second value, as there is 1st or 2nd
                bets[1] = bet_amount
                bets[0] *= 2

        # We double both values if we haven't won
        if not win:
            bets[0] *= 2
            bets[1] *= 2

        total_revenue += round_result

        result = {
            'round_num': r_num + 1,
            'roll': roll,
            'win': win,
            'bet_amount_first': old_bets[0],
            'bet_amount_second': old_bets[1],
            'result_amount': round_result,
            'total_revenue': total_revenue
        }
        results.append(result)

    return results

def calculate_win_rate(roulette_type, bet_amount, num_rolls, sets_of_12):
    win_count = 0
    revenue = 0
    for x in range(500):
        revenue_round = simulate_roulette(roulette_type, bet_amount, num_rolls, sets_of_12)[-1]['total_revenue']
        revenue += revenue_round
        if (revenue_round > 0):
            win_count += 1
    win_percentage = win_count / 500
    revenue_average = revenue / 500

    return "Win Percentage: " + str(win_percentage) + "\n Average Revenue per Round: " + str(revenue_average)

# result = []
# for i in range(300):
#     result.append(simulate_roulette("American", 1, 50, ['2nd12', '3rd12']))

# total_winnings = 0
# for x in result:
#     total_winnings += x[-1]['total_revenue']

# print("Average Win: " + str(total_winnings / 50))

######################################################################

@app.route('/simulate', methods=['POST'])
def simulate():
    data = request.json

    print(f"Received data: {data}")

    roulette_type = data.get('rouletteType')
    bet_amount = data.get('betAmount')
    num_rolls = data.get('numRolls')
    sets_of_12 = data.get('setsOf12')

    results = calculate_win_rate(roulette_type, bet_amount, num_rolls, sets_of_12)
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)