# pdf_maker.py

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.colors import HexColor, Color
import pandas as pd
from reportlab.platypus import Table, TableStyle
from procedure_fetch import fetch_data_from_procedure

def draw_header(c):
    """
    Draws the header section of the PDF, including the logo and bank information.

    Parameters:
        c (canvas.Canvas): The ReportLab canvas object.
    """
    header_color = Color(11/255, 83/255, 157/255)
    c.setFont("Helvetica-Bold", 18)
    header_x_position = 580
    c.setFillColor(header_color)
    c.drawRightString(header_x_position, 750, "BANK OF KIGALI")
    c.drawRightString(header_x_position - 180, 630, "BANK STATEMENT")
    c.setFont("Helvetica", 9)
    c.drawRightString(header_x_position, 735, "www.bk.rw")
    c.drawRightString(header_x_position, 723, "bk@bk.rw")
    c.drawRightString(header_x_position, 711, "(+350) 252 593 100")
    c.drawRightString(header_x_position, 700, "@Bank of Kigali")
    c.drawRightString(header_x_position, 688, "+250 788 319 112")
    
    logo_path = "download (1).png"  # Ensure this file exists in your project directory
    logo_x_position = 30
    logo_y_position = 700  
    logo_width = 220  
    logo_height = 55 
    try:
        c.drawImage(logo_path, logo_x_position, logo_y_position, width=logo_width, height=logo_height)
    except Exception as e:
        print(f"Error loading logo image: {e}")

def draw_account_info(c, dataframe):
    """
    Draws the account information section of the PDF.

    Parameters:
        c (canvas.Canvas): The ReportLab canvas object.
        dataframe (pd.DataFrame): The DataFrame containing account information.
    """
    header_x_position = 560
    line_height = 20 
    padding = 10 
    
    try:
        account_name = dataframe['Account Name'].iloc[0]
        account_number = dataframe['Account Number'].iloc[0]
        account_type = dataframe['Account Type'].iloc[0]
        currency = dataframe['Currency'].iloc[0]

        total_credits = dataframe['Credit'].iloc[-1]  
        total_debits = dataframe['Debit'].iloc[-1]  
        opening_balance = dataframe['Balance'].iloc[0]  
        closing_balance = dataframe['Balance'].iloc[-1]  

        transaction_count = len(dataframe) - 3  # Adjust based on your data structure

        left_side_keys = ["Account Name:", "Account:", "Account Type:", "Branch:", "Currency:", "IBN:"]
        right_side_keys = ["Opening Balance:", "Total Credits:", "Total Debits:", "Closing Balance:"]

        left_side_values = [account_name, account_number, account_type, "HQ", currency, ""]
        right_side_values = [opening_balance, total_credits, total_debits, closing_balance]
        
        y_position = 600  
        for key, value in zip(left_side_keys, left_side_values):
            c.drawString(50, y_position, key)
            c.drawString(130, y_position, str(value))
            y_position -= line_height
            
        y_position = 600  
        for key, value in zip(right_side_keys, right_side_values):
            c.drawString(350, y_position, key)
            c.drawString(header_x_position - 100, y_position, str(value))
            y_position -= line_height
        
        # Draw lines for section separation
        c.setLineWidth(0.5)
        c.line(40, 620, header_x_position + 20, 620)  
        c.line(40, 490, header_x_position + 20, 490)
        c.line(580, 490, header_x_position + 20, 620)
        c.line(40, 490, 40, 620)

        # Vertical borders
        c.line(120, 490, 120, 620)
        c.line(340, 490, 340, 620)
        c.line(430, 490, 430, 620)

        # Horizontal borders
        c.line(40, 595, header_x_position + 20, 595)
        c.line(40, 575, header_x_position + 20, 575)
        c.line(40, 555, header_x_position + 20, 555)
        c.line(40, 535, header_x_position + 20, 535)
        c.line(40, 515, 340, 515)

        # Transaction count and date lines
        c.line(40, 465, header_x_position + 20, 465)
        c.line(40, 435, header_x_position + 20, 435)
        
        # Transactional count
        c.drawString(45, 445, "Transaction Count :")
        c.drawString(160, 445, str(transaction_count))
        c.line(40, 465, 40, 435)

        # Starting Date
        c.drawString(190, 445, "Starting Date :")
        c.drawString(280, 445, dataframe['Book Date'].min().strftime('%Y-%m-%d') if not dataframe.empty else "")
        c.line(185, 465, 185, 435)

        # Ending Date
        c.drawString(400, 445, "Ending Date :")
        c.drawString(490, 445, dataframe['Book Date'].max().strftime('%Y-%m-%d') if not dataframe.empty else "")
        c.line(395, 465, 395, 435)
        c.line(580, 465, 580, 435)
    except KeyError as e:
        print(f"Missing expected column in dataframe: {e}")
    except Exception as e:
        print(f"Error drawing account info: {e}")

def draw_table(c, y_start, dataframe):
    """
    Draws the transactions table in the PDF.

    Parameters:
        c (canvas.Canvas): The ReportLab canvas object.
        y_start (int): The y-coordinate to start drawing the table.
        dataframe (pd.DataFrame): The DataFrame containing transaction data.
    """
    max_width = letter[0] - 60
    transaction_header = ['Book Date', 'Reference', 'Narration', 'Value Date', 'Credit', 'Debit', 'Balance']
    
    if not all(col in dataframe.columns for col in transaction_header):
        print("Dataframe does not contain all required columns for the table.")
        return
    
    transaction_data = dataframe[transaction_header]
    data_rows = [transaction_header] + transaction_data.values.tolist()
    
    first_page_rows = 10
    subsequent_page_rows = 17 
    
    first_chunk = data_rows[:first_page_rows + 1] 
    remaining_data = data_rows[first_page_rows + 1:]  
    
    draw_chunk(c, y_start, first_chunk, max_width, True, transaction_header)
    
    while remaining_data:
        c.showPage()  
        chunk = remaining_data[:subsequent_page_rows]
        remaining_data = remaining_data[subsequent_page_rows:]
        
        # New pages start drawing at y_start of 750
        draw_chunk(c, 750, chunk, max_width, False, transaction_header)
        draw_footer(c)

def draw_chunk(c, y_start, chunk, max_width, include_header, header):
    """
    Draws a chunk of the table on the PDF.

    Parameters:
        c (canvas.Canvas): The ReportLab canvas object.
        y_start (int): The y-coordinate to start drawing the table.
        chunk (list): The list of rows to include in the table.
        max_width (int): The maximum width of the table.
        include_header (bool): Whether to include the header row styling.
        header (list): The header row content.
    """
    num_columns = len(header)
    
    # Initial column widths: equally distributed
    equal_column_width = max_width / num_columns
    col_widths = [equal_column_width for _ in range(num_columns)]

    # Adjust specific columns
    col_widths[0] = 0.50 * equal_column_width  # Book Date
    col_widths[1] = 1.1 * equal_column_width   # Reference
    col_widths[2] = 2.5 * equal_column_width   # Narration
    col_widths[3] = 0.50 * equal_column_width  # Value Date
    col_widths[4] = 0.75 * equal_column_width  # Credit
    col_widths[5] = 0.75 * equal_column_width  # Debit
    col_widths[6] = 0.75 * equal_column_width  # Balance

    table_style_commands = [
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.white),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.white),        
    ]

    # Header-specific styles
    if include_header:
        header_style_commands = [
            ('BACKGROUND', (0, 0), (-1, 0), Color(11/255, 83/255, 157/255)),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ]
        table_style_commands.extend(header_style_commands)
    
    # Background color for data rows
    light_gray = HexColor('#F0F0F0')
    slightly_darker_gray = HexColor('#E0E0E0') 

    start_index = 1 if include_header else 0
    for index in range(len(chunk))[start_index:]:
        bg_color = light_gray if index % 2 == 1 else slightly_darker_gray
        table_style_commands.append(('BACKGROUND', (0, index), (-1, index), bg_color))

    # Create the Table object
    table = Table(chunk, colWidths=col_widths)
    table.setStyle(TableStyle(table_style_commands))
    
    # Calculate table height and draw
    table_height = table.wrapOn(c, max_width, y_start)[1]
    table.drawOn(c, 40, y_start - table_height)

def draw_footer(c):
    """
    Draws the footer section of the PDF, including the page number.

    Parameters:
        c (canvas.Canvas): The ReportLab canvas object.
    """
    page_num_text = f"Page {c.getPageNumber()}"
    footer_x_position = letter[0] - 40
    footer_y_position = 15
    c.setFont("Helvetica", 9)
    c.drawString(footer_x_position - 50, footer_y_position, page_num_text)

def create_bank_statement(filename, dataframe, account_number, start_date, end_date):
    """
    Creates the bank statement PDF.

    Parameters:
        filename (str): The name of the PDF file to create.
        dataframe (pd.DataFrame): The DataFrame containing transaction data.
        account_number (str): The account number.
        start_date (str): The start date.
        end_date (str): The end date.
    """
    c = canvas.Canvas(filename, pagesize=letter)
    
    # Draw header
    draw_header(c)
    
    # Draw account info
    draw_account_info(c, dataframe)
    
    # Starting y position for the table
    y_start = 415  
    
    # Draw table
    draw_table(c, y_start, dataframe)
    
    # Draw footer on the first page
    draw_footer(c)
    
    c.save()

def main():
    """
    Main function to execute the PDF generation process.
    """
    import argparse

    parser = argparse.ArgumentParser(description="Generate Bank Statement PDF.")
    parser.add_argument('--account', required=True, help='Account Number')
    parser.add_argument('--start', required=True, help='Start Date (YYYY-MM-DD)')
    parser.add_argument('--end', required=True, help='End Date (YYYY-MM-DD)')
    parser.add_argument('--logo', default="download (1).png", help='Path to the logo image')
    
    args = parser.parse_args()
    
    account_number = args.account
    start_date = args.start
    end_date = args.end
    logo_path = args.logo

    # Update the logo path in draw_header
    global draw_header
    original_draw_header = draw_header  # Keep original function

    def draw_header_updated(c):
        """
        Updated draw_header function to use a custom logo path.
        """
        header_color = Color(11/255, 83/255, 157/255)
        c.setFont("Helvetica-Bold", 18)
        header_x_position = 580
        c.setFillColor(header_color)
        c.drawRightString(header_x_position, 750, "BANK OF KIGALI")
        c.drawRightString(header_x_position - 180, 630, "BANK STATEMENT")
        c.setFont("Helvetica", 9)
        c.drawRightString(header_x_position, 735, "www.bk.rw")
        c.drawRightString(header_x_position, 723, "bk@bk.rw")
        c.drawRightString(header_x_position, 711, "(+350) 252 593 100")
        c.drawRightString(header_x_position, 700, "@Bank of Kigali")
        c.drawRightString(header_x_position, 688, "+250 788 319 112")
        
        logo_x_position = 30
        logo_y_position = 700  
        logo_width = 220  
        logo_height = 55 
        try:
            c.drawImage(logo_path, logo_x_position, logo_y_position, width=logo_width, height=logo_height)
        except Exception as e:
            print(f"Error loading logo image: {e}")
    
    draw_header = draw_header_updated  # Override the draw_header function

    # Fetch data
    dataframe, acc_num, start, end = fetch_data_from_procedure(account_number, start_date, end_date)
    
    if dataframe.empty:
        print("No data retrieved. PDF will not be generated.")
        return
    
    # Define PDF filename
    filename = f"Bank_Statement_{acc_num}_{start}_to_{end}.pdf"
    
    # Create PDF
    create_bank_statement(filename, dataframe, acc_num, start, end)
    
    print(f"Bank statement has been saved as {filename}")

if __name__ == "__main__":
    main()
