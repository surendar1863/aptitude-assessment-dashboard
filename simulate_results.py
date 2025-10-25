import pandas as pd
import random

# Simulate 300 students
num_students = 300
names = [f"Student_{i}" for i in range(1, num_students + 1)]
rolls = [f"24BCAR{i:03d}" for i in range(1, num_students + 1)]

# Random scores between 0 and 10
scores = [random.randint(0, 10) for _ in range(num_students)]

# Create DataFrame
df = pd.DataFrame({
    "Name": names,
    "Roll": rolls,
    "Score": scores,
    "Total": 10
})

# Save to CSV
df.to_csv("results.csv", index=False)
print("✅ 300 simulated student results saved to results.csv")
