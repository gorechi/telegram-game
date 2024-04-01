from functions import roll

dex = 4
intel = 1
stren = 10
mastery = 1
base_price = 7
base_price_die = 8
dice = []
for _ in range(mastery):
    dice.append(base_price_die)



for _ in range (50):
    print(roll(dice) + base_price)
