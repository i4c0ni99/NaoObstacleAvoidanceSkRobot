import matplotlib.pyplot as plt

def generate_burndown_chart(total_points, sprint_length, actual_points):
    # Genera la lista dei giorni della sprint
    days = list(range(1, sprint_length + 1))

    # Genera i punti target per ogni giorno
    
    target_points = [total_points + 3  - (total_points  / sprint_length) * day for day in days]
    print(target_points)
    
    # Plot del burn down chart
    plt.figure(figsize=(15, 5))
    plt.plot(days, target_points, label='Target Points', color='blue', linestyle='--', marker='o')
    plt.plot(days, actual_points, label='Actual Points', color='green', marker='o')
    plt.title('Burn Down Chart')
    plt.xlabel('Day')
    plt.ylabel('Story Points')
    plt.legend()
    plt.grid(True)
    plt.xticks(days)
    plt.yticks(range(0, total_points + 1, 5))
    plt.tight_layout()
    plt.show()
    
# Parametri della sprint
total_points = 79  # Totale degli story points della sprint
sprint_length = 15  # Lunghezza della sprint in giorni

# Story points completati per ogni giorno (esempio)
actual_points = [77,72,59,54, 51, 48, 40, 37, 29, 21,13,10,8,5,0]

# Genera e visualizza il burn down chart
generate_burndown_chart(total_points, sprint_length, actual_points)