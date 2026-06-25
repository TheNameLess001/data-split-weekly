import streamlit as st
import pandas as pd
import zipfile
import io

st.set_page_config(page_title="Weekly Data Splitter", layout="centered")

st.title("📅 Weekly Data Splitter")
st.write("Upload your export CSV, and this app will split it into weekly files (Monday to Sunday) and pack them into a single ZIP for easy download.")

# File uploader
uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file is not None:
    try:
        # 1. Read the uploaded CSV
        df = pd.read_csv(uploaded_file)
        
        st.write("### Data Preview")
        st.dataframe(df.head())
        
        # 2. Identify the date column based on the provided mapping
        date_col = 'order day'
        
        if date_col not in df.columns:
            st.error(f"Error: Could not find the '{date_col}' column in the uploaded file. Please check your CSV.")
        else:
            with st.spinner("Processing and splitting data..."):
                # Convert the 'order day' column to datetime objects
                df[date_col] = pd.to_datetime(df[date_col])
                
                # Get the ISO week number (ISO weeks start on Monday and end on Sunday)
                # We also get the year to prevent mixing weeks if data spans across different years
                df['Week_Number'] = df[date_col].dt.isocalendar().week
                df['Year'] = df[date_col].dt.isocalendar().year
                
                # Group the data by Year and Week Number
                grouped = df.groupby(['Year', 'Week_Number'])
                
                # 3. Create an in-memory ZIP file buffer
                zip_buffer = io.BytesIO()
                
                with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                    for (year, week), group in grouped:
                        # Drop the temporary Week and Year columns before exporting
                        clean_group = group.drop(columns=['Week_Number', 'Year'])
                        
                        # Convert the week's dataframe to CSV format in memory
                        csv_data = clean_group.to_csv(index=False)
                        
                        # Create the requested file name: "data week x.csv"
                        # Added year to the name to avoid overwriting if the file has data from multiple years
                        file_name = f"data week {week}_{year}.csv"
                        
                        # Write the CSV data into the ZIP file
                        zip_file.writestr(file_name, csv_data)
                
                st.success("✅ Data successfully split by week!")
                
                # 4. Provide the 1-click download button for the ZIP
                st.download_button(
                    label="📥 Download All Weekly Files (ZIP)",
                    data=zip_buffer.getvalue(),
                    file_name="weekly_data_export.zip",
                    mime="application/zip",
                    use_container_width=True
                )
                
    except Exception as e:
        st.error(f"An error occurred while processing the file: {e}")
