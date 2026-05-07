# My Simple Tracker

My Simple Tracker is a local goal-tracking app for following progress, consistency, streaks, notes, exceptions, mood, and statistics.

It runs on your computer and opens in your browser. No account, database, or external service is required.

## Features

- Create goals with a custom color.
- Choose a cadence: daily, weekdays, weekly, or custom.
- Track custom goals like `3 times per week` or `5 times per month`.
- Add an optional goal end date.
- Mark goals complete from the selected calendar day.
- Add notes for goal completions.
- Add exceptions such as vacation, sick, commuting, mental break, or other.
- Track daily emotional status separately from goals.
- See a consistency calendar with goal colors, exceptions, moods, and end dates.
- View streaks and monthly completion progress.
- Use the Stats page for daily, weekly, monthly, yearly, or custom date ranges.
- Filter statistics by goal.
- View charts for trends, completion rates, checks by goal, emotions, and exceptions.
- Switch between themes: Neutral, Pink, Light blue, Dark, Sunrise, and Twilight.
- Reset all local tracker data with confirmation.

## How It Works

The app starts a tiny local web server on:

```text
http://127.0.0.1:8787
```

Opening the app launches that local page in your browser. The stable port keeps your browser storage connected to the same app address each time.

Your tracker records are stored in your browser's local storage. This includes:

- goals
- completions
- notes
- exceptions
- emotional status
- selected theme

Because the data is local browser storage, it is not pushed to GitHub and is not included in the app code.

## Run From Terminal

```bash
python3 my_simple_tracker.py
```

Then open:

```text
http://127.0.0.1:8787
```

## macOS App

A lightweight macOS app wrapper is included:

```text
mac-app/My Simple Tracker.app
```

Open it to start the local tracker server and launch the app in your browser.

This wrapper is intentionally simple: it runs the bundled Python tracker script. It is not a signed or notarized distributable macOS app.

## Privacy

The app is private in the sense that it runs locally and your records stay in your browser on your machine.

Important caveats:

- Clearing browser data can erase your tracker records.
- A different browser profile will have different saved data.
- Anyone with access to your computer/browser profile may be able to see the data.
- The app does not currently encrypt records.

## Project Structure

```text
.
├── my_simple_tracker.py
├── mac-app/
│   ├── My Simple Tracker.app/
│   ├── README.md
│   └── tracker-icon-master.png
└── README.md
```

## Repository

```text
https://github.com/SofiaPadovaniPlazzi/My-Simple-Tracker
```
