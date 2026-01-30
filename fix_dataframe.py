import re

# Read the file
with open(r'C:\Users\Ayan Parmar\Desktop\NestTry\src\dashboard\app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace st.dataframe(..., width='stretch') with st.dataframe(..., use_container_width=True)
new_content = re.sub(r"st\.dataframe\(([^)]+), width='stretch'\)", r"st.dataframe(\1, use_container_width=True)", content)

# Write back
with open(r'C:\Users\Ayan Parmar\Desktop\NestTry\src\dashboard\app.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Fixed all st.dataframe calls")
