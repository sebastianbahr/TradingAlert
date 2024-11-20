import pandas as pd

import smtplib
from email.message import EmailMessage


class EmailSender:
    
  def __init__(self, entries: pd.DataFrame, exits: pd.DataFrame, server: str, port: int, email_pw: str, sender: str, receiver: str):
      self.entries = entries
      self.exits = exits
      self.server = server
      self.port = port
      self.email_pw = email_pw
      self.sender = sender
      self.receiver = receiver
        

  def create_table(self, df: pd.DataFrame, entry: bool):
    # create html table that is used in email
    table = []

    if entry == True:
        for i in range(len(df)):
            table.append(
                f"""<tr>
                        <th style="text-align:left">{df.iloc[i].ticker}</th>
                        <th style="text-align:left">{df.iloc[i].date}</th>
                        <th style="text-align:left">{', '.join(df.iloc[i].strategy)}</th>
                        <th style="text-align:left">{round(df.iloc[i].open, 2)}</th>
                        <th style="text-align:left">{round(df.iloc[i].close, 2)}</th>
                        <th style="text-align:left">{df.iloc[i].entry_market}</th>
                        <th style="text-align:left">{round(df.iloc[i].stop_loss, 2)}</th>
                        <th style="text-align:left">{round(df.iloc[i].stop_rrr, 2)}</th>
                </tr>"""
            )

    else:
         for i in range(len(df)):
            table.append(
                f"""<tr>
                        <th style="text-align:left">{df.iloc[i].ticker}</th>
                        <th style="text-align:left">{df.iloc[i].date}</th>
                        <th style="text-align:left">{round(df.iloc[i].open, 2)}</th>
                        <th style="text-align:left">{round(df.iloc[i].close, 2)}</th>
                        <th style="text-align:left">{round(df.iloc[i].approx_gain_ps, 2)}</th>
                </tr>"""
            )

    table = [x.replace('\n', '') for x in table]
    return table


  def send_email(self):      
    self.entries_table = self.create_table(self.entries, True)
    self.exits_table = self.create_table(self.exits, False)

    entries_text = f"""<table style="width:700px">
                            <tr>
                              <th style="text-align:left; width:5%"><strong>Ticker</strong></th>
                              <th style="text-align:left; width:15%"><strong>Date</strong></th>
                              <th style="text-align:left; width:10%"><strong>Strategy</strong></th>
                              <th style="text-align:left; width:5%"><strong>Open</strong></th>
                              <th style="text-align:left; width:5%"><strong>Close</strong></th>
                              <th style="text-align:left; width:12%"><strong>Entry Market</strong></th>
                              <th style="text-align:left; width:5%"><strong>Stop Loss</strong></th>
                              <th style="text-align:left; width:5%"><strong>Stop RRR</strong></th>
                            </tr>
                            {''.join(self.entries_table)}
                        </table>"""
    exits_text = f"""<table style="width:500px">
                            <tr>
                              <th style="text-align:left; width:5%"><strong>Ticker</strong></th>
                              <th style="text-align:left; width:15%"><strong>Date</strong></th>
                              <th style="text-align:left; width:5%"><strong>Open</strong></th>
                              <th style="text-align:left; width:5%"><strong>Close</strong></th>
                              <th style="text-align:left; width:10%"><strong>~ Gain per share</strong></th>
                            </tr>
                            {''.join(self.exits_table)}
                        </table>"""

    subject = "Your Trading Update 🚀"

    if len(self.entries) == 0:
       entries_text = "No entries found today."

    if len(self.exits) == 0:
       exits_text = "No exits found today."

    message_body = (
        "<html>"
        "<style>"
        """table {
          border-collapse: collapse;
          width: 100%;
        }"""
        """tr {
          border-bottom: 1px solid #ddd;
        }"""
        "</style>"
        "<font size='2' face='Courier New' >"
        "<body>"
        "<p>Good morning! Here's your daily trading update:</p>"
        "<br/"
        "<p>---- Possible entries to consider ----</p>"
        f"{entries_text}"
        "<br/"
        "<br/"
        "<p>---- Exits to perform tomorrow ----</p>"
        f"<p>{exits_text}</p>"
        "<br/"
        "<p>Have a great rest of your day!</p>"
        "</body>"
        "</html>"
    )


    try:
        email = EmailMessage()
        email["From"] = self.sender
        email["To"] = self.receiver  # sending email to myself
        email["Subject"] = subject
        email.set_content("This is a plain text fallback in case HTML is not supported.")
        email.add_alternative(message_body, subtype='html')

        with smtplib.SMTP_SSL(self.server, port=self.port) as smtp:
            smtp.login(self.sender, self.email_pw)
            smtp.send_message(email)
        print("Email sent successfully.")
    except Exception as e:
        print(f"Failed to send email. Error: {e}")