from http.server import BaseHTTPRequestHandler, HTTPServer
from socket import error as SocketError
from socketserver import ThreadingMixIn
import webbrowser


APP_HTML = r"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Goal Progress Tracker</title>
  <style>
    :root {
      color-scheme: light;
      --bg: #f7f7f2;
      --ink: #252525;
      --muted: #666a73;
      --line: #deded4;
      --panel: #ffffff;
      --side: #fcfcf8;
      --field: #ffffff;
      --soft: #fbfbf7;
      --track: #f1f0e8;
      --accent: #287c74;
      --accent-ink: #ffffff;
      --danger: #b84242;
      --shadow: 0 14px 35px rgba(39, 45, 50, 0.12);
    }

    body[data-theme="pink"] {
      --bg: #fff5f8;
      --ink: #34232b;
      --muted: #80636e;
      --line: #efd1dc;
      --panel: #ffffff;
      --side: #fff0f5;
      --field: #ffffff;
      --soft: #fff7fa;
      --track: #f6dce6;
      --accent: #c84f7a;
      --danger: #a94355;
      --shadow: 0 14px 35px rgba(99, 45, 68, 0.12);
    }

    body[data-theme="light_blue"] {
      --bg: #f2f8ff;
      --ink: #213040;
      --muted: #5f7184;
      --line: #cfe1ef;
      --panel: #ffffff;
      --side: #edf6ff;
      --field: #ffffff;
      --soft: #f7fbff;
      --track: #dbeaf6;
      --accent: #347da8;
      --danger: #b14c52;
      --shadow: 0 14px 35px rgba(42, 84, 116, 0.12);
    }

    body[data-theme="dark"] {
      color-scheme: dark;
      --bg: #161719;
      --ink: #f2f0ea;
      --muted: #aaa69d;
      --line: #33363b;
      --panel: #202226;
      --side: #1c1e22;
      --field: #26292e;
      --soft: #25282d;
      --track: #33363b;
      --accent: #69b8a9;
      --danger: #e07a7a;
      --shadow: 0 14px 35px rgba(0, 0, 0, 0.32);
    }

    body[data-theme="sunrise"] {
      --bg: #fff7ed;
      --ink: #39291f;
      --muted: #7d6557;
      --line: #efd6bd;
      --panel: #ffffff;
      --side: #fff1df;
      --field: #ffffff;
      --soft: #fff9f1;
      --track: #f6dfc8;
      --accent: #d36c42;
      --danger: #b84242;
      --shadow: 0 14px 35px rgba(128, 80, 44, 0.13);
    }

    body[data-theme="twilight"] {
      color-scheme: dark;
      --bg: #171426;
      --ink: #f4eefc;
      --muted: #b9abc9;
      --line: #3a314f;
      --panel: #211d32;
      --side: #1c182b;
      --field: #2a243d;
      --soft: #28233a;
      --track: #3b3351;
      --accent: #b28dff;
      --danger: #ff8e9e;
      --shadow: 0 14px 35px rgba(5, 3, 15, 0.38);
    }

    * { box-sizing: border-box; }

    body {
      margin: 0;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: var(--bg);
      color: var(--ink);
    }

    button, input, select, textarea {
      font: inherit;
    }

    button {
      border: 0;
      cursor: pointer;
    }

    .app {
      min-height: 100vh;
      display: grid;
      grid-template-columns: 320px minmax(0, 1fr);
    }

    .app.stats-mode {
      grid-template-columns: 1fr;
    }

    .app.stats-mode aside {
      display: none;
    }

    aside {
      min-height: 100vh;
      padding: 24px;
      border-right: 1px solid var(--line);
      background: var(--side);
    }

    main {
      padding: 24px;
      overflow: hidden;
    }

    .brand {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      margin-bottom: 24px;
    }

    h1 {
      margin: 0;
      font-size: 22px;
      letter-spacing: 0;
    }

    h2 {
      margin: 0;
      font-size: 17px;
      letter-spacing: 0;
    }

    .today {
      color: var(--muted);
      font-size: 13px;
      margin-top: 4px;
    }

    .form {
      display: grid;
      gap: 10px;
      margin-bottom: 24px;
    }

    .field {
      display: grid;
      gap: 6px;
    }

    label {
      color: var(--muted);
      font-size: 12px;
      font-weight: 700;
      text-transform: uppercase;
    }

    input, select, textarea {
      width: 100%;
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 10px 11px;
      background: var(--field);
      color: var(--ink);
      outline: none;
    }

    textarea {
      min-height: 86px;
      resize: vertical;
    }

    input:focus, select:focus, textarea:focus {
      border-color: var(--accent);
      box-shadow: 0 0 0 3px rgba(40, 124, 116, 0.14);
    }

    .row {
      display: grid;
      grid-template-columns: 1fr 76px;
      gap: 10px;
    }

    .custom-cadence {
      display: none;
      grid-template-columns: 96px 1fr;
      gap: 10px;
    }

    .custom-cadence.visible {
      display: grid;
    }

    input[type="color"] {
      height: 42px;
      padding: 3px;
      cursor: pointer;
    }

    input[type="color"]::-webkit-color-swatch-wrapper {
      padding: 0;
    }

    input[type="color"]::-webkit-color-swatch {
      border: 0;
      border-radius: 5px;
    }

    input[type="color"]::-moz-color-swatch {
      border: 0;
      border-radius: 5px;
    }

    .primary {
      min-height: 42px;
      border-radius: 8px;
      background: var(--accent);
      color: var(--accent-ink);
      font-weight: 800;
    }

    .ghost {
      min-width: 36px;
      min-height: 36px;
      border-radius: 8px;
      border: 1px solid var(--line);
      background: var(--field);
      color: var(--ink);
    }

    .goal-list {
      display: grid;
      gap: 8px;
    }

    .goal-button {
      width: 100%;
      display: grid;
      grid-template-columns: 12px minmax(0, 1fr) auto;
      align-items: center;
      gap: 10px;
      padding: 10px;
      border-radius: 8px;
      background: transparent;
      color: var(--ink);
      text-align: left;
    }

    .goal-button.active,
    .goal-button:hover {
      background: color-mix(in srgb, var(--accent) 12%, var(--field));
    }

    .swatch {
      width: 12px;
      height: 28px;
      border-radius: 999px;
    }

    .goal-name {
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
      font-weight: 800;
    }

    .goal-meta {
      color: var(--muted);
      font-size: 12px;
    }

    .summary {
      display: grid;
      grid-template-columns: repeat(4, minmax(150px, 1fr));
      gap: 12px;
      margin-bottom: 18px;
    }

    .page-tabs {
      display: inline-grid;
      grid-template-columns: 1fr 1fr;
      gap: 4px;
      padding: 4px;
      margin-bottom: 18px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--field);
    }

    .topbar {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 12px;
      margin-bottom: 18px;
    }

    .topbar .page-tabs {
      margin-bottom: 0;
    }

    .topbar-actions {
      display: flex;
      align-items: center;
      gap: 8px;
      flex-wrap: wrap;
      justify-content: flex-end;
    }

    .theme-control {
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .theme-control label {
      white-space: nowrap;
    }

    .theme-control select {
      min-width: 142px;
    }

    .reset-button {
      position: fixed;
      left: 18px;
      bottom: 18px;
      z-index: 20;
      min-height: 38px;
      padding: 0 12px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--field);
      color: var(--danger);
      box-shadow: var(--shadow);
      font-weight: 900;
    }

    .reset-button:hover {
      border-color: var(--danger);
    }

    .password-button {
      min-height: 42px;
      padding: 0 12px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--field);
      color: var(--ink);
      font-weight: 900;
    }

    .password-button.active {
      border-color: var(--accent);
      box-shadow: inset 0 -3px 0 var(--accent);
    }

    .pin-overlay {
      position: fixed;
      inset: 0;
      z-index: 50;
      display: none;
      align-items: center;
      justify-content: center;
      padding: 24px;
      background: color-mix(in srgb, var(--bg) 72%, rgba(0, 0, 0, 0.48));
      backdrop-filter: blur(10px);
    }

    .pin-overlay.visible {
      display: flex;
    }

    .pin-card {
      width: min(360px, 100%);
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--panel);
      box-shadow: var(--shadow);
      padding: 20px;
    }

    .pin-head {
      display: flex;
      align-items: start;
      justify-content: space-between;
      gap: 12px;
      margin-bottom: 16px;
    }

    .pin-subtitle {
      margin-top: 4px;
      color: var(--muted);
      font-size: 13px;
    }

    .pin-dots {
      display: flex;
      justify-content: center;
      gap: 10px;
      margin-bottom: 16px;
    }

    .pin-dot {
      width: 14px;
      height: 14px;
      border: 2px solid var(--line);
      border-radius: 99px;
      background: transparent;
    }

    .pin-dot.filled {
      border-color: var(--accent);
      background: var(--accent);
    }

    .pin-pad {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 8px;
    }

    .pin-key {
      min-height: 54px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--field);
      color: var(--ink);
      font-size: 20px;
      font-weight: 900;
    }

    .pin-key:hover {
      border-color: var(--accent);
      background: color-mix(in srgb, var(--accent) 10%, var(--field));
    }

    .pin-actions {
      display: grid;
      gap: 8px;
      margin-top: 12px;
    }

    .pin-message {
      min-height: 20px;
      margin: 8px 0 0;
      color: var(--danger);
      font-size: 13px;
      font-weight: 800;
      text-align: center;
    }

    .page-tab {
      min-height: 34px;
      padding: 0 14px;
      border-radius: 6px;
      background: transparent;
      color: var(--muted);
      font-weight: 800;
    }

    .page-tab.active {
      background: var(--ink);
      color: var(--bg);
    }

    .page {
      display: none;
    }

    .page.active {
      display: block;
    }

    .stat, .panel {
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--panel);
      box-shadow: var(--shadow);
    }

    .stat {
      padding: 16px;
    }

    .stat strong {
      display: block;
      font-size: 30px;
      line-height: 1;
      margin-bottom: 8px;
    }

    .stat span {
      color: var(--muted);
      font-size: 13px;
    }

    .workspace {
      display: grid;
      grid-template-columns: minmax(0, 1.35fr) minmax(320px, 0.75fr);
      gap: 18px;
      align-items: start;
    }

    .panel {
      padding: 18px;
      min-width: 0;
    }

    .panel-head {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      margin-bottom: 14px;
    }

    .month-nav {
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .month-title {
      width: 154px;
      text-align: center;
      font-weight: 900;
    }

    .weekdays, .calendar {
      display: grid;
      grid-template-columns: repeat(7, minmax(0, 1fr));
      gap: 8px;
    }

    .weekdays {
      color: var(--muted);
      font-size: 12px;
      font-weight: 800;
      margin-bottom: 8px;
      text-align: center;
      text-transform: uppercase;
    }

    .day {
      position: relative;
      min-height: 78px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--soft);
      padding: 8px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      transition: transform 140ms ease, border-color 140ms ease;
    }

    .day:not(.blank):hover {
      border-color: var(--accent);
      transform: translateY(-1px);
    }

    .day.blank {
      background: transparent;
      border-color: transparent;
    }

    .day.today {
      outline: 3px solid rgba(40, 124, 116, 0.18);
    }

    .day.selected {
      border-color: var(--accent);
      box-shadow: 0 0 0 3px rgba(40, 124, 116, 0.12);
    }

    .day.end-date {
      border-width: 3px;
      border-color: var(--end-color, var(--ink));
    }

    .date-number {
      font-weight: 900;
      font-size: 13px;
    }

    .marks {
      display: flex;
      flex-wrap: wrap;
      gap: 4px;
      min-height: 16px;
    }

    .mark {
      width: 10px;
      height: 10px;
      border-radius: 99px;
    }

    .exception-mark {
      display: inline-block;
      box-sizing: border-box;
      width: 10px;
      height: 10px;
      border: 2px solid currentColor;
      border-radius: 99px;
      background: transparent;
    }

    .emotion-mark {
      margin-left: auto;
      color: var(--muted);
      display: inline-flex;
      align-items: center;
      justify-content: center;
    }

    .emotion-mark svg {
      width: 16px;
      height: 16px;
    }

    .emotion-tracker {
      margin-top: 16px;
      padding-top: 14px;
      border-top: 1px solid var(--line);
    }

    .emotion-buttons {
      display: grid;
      grid-template-columns: repeat(6, minmax(36px, 1fr));
      gap: 8px;
    }

    .emotion-button {
      min-height: 56px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--field);
      color: var(--ink);
      display: inline-grid;
      align-items: center;
      justify-content: center;
      gap: 3px;
      padding: 6px 4px;
    }

    .emotion-button svg {
      width: 22px;
      height: 22px;
      margin: 0 auto;
    }

    .emotion-button span {
      color: var(--muted);
      font-size: 10px;
      font-weight: 900;
      line-height: 1.1;
    }

    .emotion-button.active,
    .emotion-button:hover {
      border-color: var(--accent);
      background: color-mix(in srgb, var(--accent) 12%, var(--field));
    }

    .selected-goal {
      display: grid;
      gap: 14px;
    }

    .selected-banner {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 12px;
      background: var(--soft);
    }

    .check-button {
      width: 100%;
      min-height: 52px;
      border-radius: 8px;
      background: var(--ink);
      color: var(--bg);
      font-weight: 900;
    }

    .check-button.done {
      background: var(--accent);
    }

    .progress-line {
      height: 10px;
      border-radius: 999px;
      background: var(--track);
      overflow: hidden;
    }

    .progress-line > span {
      display: block;
      height: 100%;
      width: 0;
      background: var(--accent);
      border-radius: inherit;
    }

    .chart {
      display: grid;
      grid-template-columns: repeat(7, minmax(0, 1fr));
      align-items: end;
      gap: 8px;
      height: 180px;
      padding-top: 12px;
    }

    .bar-wrap {
      display: grid;
      grid-template-rows: 1fr auto;
      gap: 8px;
      min-width: 0;
      height: 100%;
    }

    .bar-track {
      display: flex;
      align-items: end;
      min-height: 0;
      border-radius: 8px;
      background: var(--track);
      overflow: hidden;
    }

    .bar {
      width: 100%;
      min-height: 4px;
      background: var(--accent);
    }

    .bar-label {
      color: var(--muted);
      font-size: 11px;
      font-weight: 800;
      text-align: center;
    }

    .empty {
      padding: 40px 16px;
      border: 1px dashed var(--line);
      border-radius: 8px;
      color: var(--muted);
      text-align: center;
    }

    .danger {
      background: transparent;
      color: var(--danger);
      font-weight: 800;
    }

    .note-list {
      display: grid;
      gap: 8px;
    }

    .note-item {
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 10px;
      background: var(--soft);
    }

    .note-date {
      display: block;
      margin-bottom: 4px;
      color: var(--muted);
      font-size: 12px;
      font-weight: 800;
    }

    .note-text {
      margin: 0;
      color: var(--ink);
      font-size: 13px;
      line-height: 1.45;
      white-space: pre-wrap;
    }

    .stats-grid {
      display: grid;
      grid-template-columns: minmax(0, 1fr) minmax(320px, 0.8fr);
      gap: 18px;
      align-items: start;
    }

    .stats-controls {
      display: grid;
      gap: 14px;
      margin-bottom: 18px;
      grid-column: 1 / -1;
    }

    .control-row {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      align-items: center;
    }

    .segmented {
      display: flex;
      flex-wrap: wrap;
      gap: 4px;
      padding: 4px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--field);
    }

    .segment {
      min-height: 34px;
      padding: 0 12px;
      border-radius: 6px;
      background: transparent;
      color: var(--muted);
      font-weight: 800;
    }

    .segment.active {
      background: var(--ink);
      color: var(--bg);
    }

    .goal-filter {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }

    .goal-chip {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      min-height: 34px;
      padding: 0 10px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--field);
      color: var(--muted);
      font-weight: 800;
      cursor: pointer;
    }

    .goal-chip.active {
      border-color: var(--chip-color, var(--accent));
      color: var(--ink);
      box-shadow: inset 0 -3px 0 var(--chip-color, var(--accent));
    }

    .custom-range {
      display: none;
      grid-template-columns: repeat(2, minmax(160px, 1fr));
      gap: 10px;
    }

    .custom-range.visible {
      display: grid;
    }

    .stats-stack {
      display: grid;
      gap: 18px;
    }

    .wide-chart {
      display: grid;
      align-items: end;
      gap: 8px;
      height: 240px;
      padding-top: 12px;
    }

    .pie-wrap {
      display: grid;
      grid-template-columns: 150px minmax(0, 1fr);
      gap: 18px;
      align-items: center;
    }

    .pie {
      width: 150px;
      aspect-ratio: 1;
      border-radius: 50%;
      background: var(--track);
      border: 1px solid var(--line);
    }

    .legend {
      display: grid;
      gap: 8px;
    }

    .legend-row {
      display: grid;
      grid-template-columns: 12px minmax(0, 1fr) auto;
      align-items: center;
      gap: 8px;
      color: var(--muted);
      font-size: 13px;
      font-weight: 800;
    }

    .legend-dot {
      width: 12px;
      height: 12px;
      border-radius: 99px;
    }

    .goal-bars {
      display: grid;
      gap: 12px;
    }

    .goal-bar-row {
      display: grid;
      grid-template-columns: minmax(110px, 0.35fr) minmax(0, 1fr) 52px;
      align-items: center;
      gap: 10px;
    }

    .goal-bar-label {
      min-width: 0;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
      font-weight: 800;
      font-size: 13px;
    }

    .goal-bar-track {
      height: 12px;
      border-radius: 999px;
      background: var(--track);
      overflow: hidden;
    }

    .goal-bar-fill {
      height: 100%;
      border-radius: inherit;
    }

    .goal-bar-value {
      color: var(--muted);
      font-size: 12px;
      font-weight: 900;
      text-align: right;
    }

    .mini-list {
      display: grid;
      gap: 10px;
    }

    .mini-row {
      display: grid;
      grid-template-columns: 12px minmax(0, 1fr) auto;
      align-items: center;
      gap: 10px;
      padding-bottom: 10px;
      border-bottom: 1px solid var(--line);
    }

    .mini-row:last-child {
      padding-bottom: 0;
      border-bottom: 0;
    }

    @media (max-width: 980px) {
      .app {
        grid-template-columns: 1fr;
      }

      aside {
        min-height: auto;
        border-right: 0;
        border-bottom: 1px solid var(--line);
      }

      .summary, .workspace, .stats-grid {
        grid-template-columns: 1fr;
      }

      .pie-wrap {
        grid-template-columns: 1fr;
      }
    }

    @media (max-width: 620px) {
      aside, main {
        padding: 16px;
      }

      .topbar {
        align-items: stretch;
        flex-direction: column;
      }

      .topbar-actions {
        justify-content: stretch;
      }

      .summary {
        grid-template-columns: repeat(2, minmax(0, 1fr));
      }

      .weekdays, .calendar {
        gap: 5px;
      }

      .day {
        min-height: 56px;
        padding: 6px;
      }

      .month-title {
        width: 128px;
      }

      .custom-range {
        grid-template-columns: 1fr;
      }
    }
  </style>
</head>
<body>
  <div class="app" id="app">
    <aside>
      <div class="brand">
        <div>
          <h1>Goals</h1>
          <div class="today" id="todayLabel"></div>
        </div>
      </div>

      <form class="form" id="goalForm">
        <div class="field">
          <label for="goalName">Goal</label>
          <input id="goalName" name="goalName" placeholder="Read, train, write..." required>
        </div>
        <div class="field">
          <label for="goalEndDate">End date</label>
          <input id="goalEndDate" name="goalEndDate" type="date">
        </div>
        <div class="row">
          <div class="field">
            <label for="goalCadence">Cadence</label>
            <select id="goalCadence" name="goalCadence">
              <option value="daily">Daily</option>
              <option value="weekday">Weekdays</option>
              <option value="weekly">Weekly</option>
              <option value="custom">Custom</option>
            </select>
          </div>
          <div class="field">
            <label for="goalColor">Color</label>
            <input id="goalColor" name="goalColor" type="color" value="#287c74">
          </div>
        </div>
        <div class="custom-cadence" id="customCadence">
          <div class="field">
            <label for="goalTarget">Target</label>
            <input id="goalTarget" name="goalTarget" type="number" min="1" max="31" value="3">
          </div>
          <div class="field">
            <label for="goalTargetUnit">Every</label>
            <select id="goalTargetUnit" name="goalTargetUnit">
              <option value="week">Times per week</option>
              <option value="month">Times per month</option>
            </select>
          </div>
        </div>
        <button class="primary" type="submit">Add goal</button>
      </form>

      <div class="goal-list" id="goalList"></div>
    </aside>

    <main>
      <div class="topbar">
        <nav class="page-tabs" aria-label="Pages">
          <button class="page-tab active" id="trackerTab" type="button">Tracker</button>
          <button class="page-tab" id="statsTab" type="button">Stats</button>
        </nav>
        <div class="topbar-actions">
          <div class="theme-control">
            <label for="themeSelect">Theme</label>
            <select id="themeSelect">
              <option value="neutral">Neutral</option>
              <option value="pink">Pink</option>
              <option value="light_blue">Light blue</option>
              <option value="dark">Dark</option>
              <option value="sunrise">Sunrise</option>
              <option value="twilight">Twilight</option>
            </select>
          </div>
          <button class="password-button" id="passwordButton" type="button">Password</button>
        </div>
      </div>

      <section class="summary" id="summary"></section>

      <div class="page active" id="trackerPage">
        <div class="workspace">
        <section class="panel">
          <div class="panel-head">
            <h2>Consistency Calendar</h2>
            <div class="month-nav">
              <button class="ghost" id="prevMonth" title="Previous month" type="button">&#8249;</button>
              <div class="month-title" id="monthTitle"></div>
              <button class="ghost" id="nextMonth" title="Next month" type="button">&#8250;</button>
            </div>
          </div>
          <div class="weekdays">
            <div>Mon</div><div>Tue</div><div>Wed</div><div>Thu</div><div>Fri</div><div>Sat</div><div>Sun</div>
          </div>
          <div class="calendar" id="calendar"></div>
          <div class="emotion-tracker" id="emotionTracker"></div>
        </section>

        <section class="panel selected-goal" id="detail"></section>
        </div>
      </div>

      <div class="page" id="statsPage">
        <div class="stats-grid" id="statsDetail"></div>
      </div>
    </main>
    <button class="reset-button" id="resetButton" type="button">Reset</button>
  </div>

  <div class="pin-overlay" id="pinOverlay" aria-modal="true" role="dialog"></div>

  <script>
    const storageKey = "goal-tracker-v1";
    const palette = ["#287c74", "#c85d45", "#5a66ad", "#d79d22", "#7a4f95", "#3f7d42"];
    const exceptionTypes = {
      vacation: "Vacation",
      sick: "Sick",
      commuting: "Commuting",
      mental_break: "Mental break",
      other: "Other"
    };
    const emotionTypes = {
      energized: "Energized",
      calm: "Calm",
      okay: "Okay",
      tired: "Tired",
      stressed: "Stressed",
      low: "Low"
    };
    const emotionIcons = {
      energized: `<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="4.5" fill="none" stroke="currentColor" stroke-width="2"/><path d="M12 2.5v2.2M12 19.3v2.2M4.7 4.7l1.6 1.6M17.7 17.7l1.6 1.6M2.5 12h2.2M19.3 12h2.2M4.7 19.3l1.6-1.6M17.7 6.3l1.6-1.6" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>`,
      calm: `<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 18c6.5-.3 11.1-4.8 13.2-12.3C10.8 6.2 5.6 10.5 5 18Z" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/><path d="M5 18c3.2-2.8 6.4-4.7 9.8-5.8" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>`,
      okay: `<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="8.5" fill="none" stroke="currentColor" stroke-width="2"/><path d="M8.5 10h.1M15.4 10h.1M8.5 14.2c1.9 1.9 5.1 1.9 7 0" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>`,
      tired: `<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M15.5 3.8A7.6 7.6 0 1 0 20.2 17 8.6 8.6 0 0 1 15.5 3.8Z" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/><path d="M6.8 7.5h4.4l-4.4 4.2h4.4M14.8 15.5h3.5l-3.5 3.3h3.5" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>`,
      stressed: `<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M7.5 17.8a5 5 0 0 1 .6-9.9 6.2 6.2 0 0 1 11.6 3.1 3.9 3.9 0 0 1-1.1 7.6H7.5Z" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/><path d="M11.5 11.4 10 14h2.3l-1.1 3" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>`,
      low: `<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3.5" y="8" width="15" height="8" rx="2" fill="none" stroke="currentColor" stroke-width="2"/><path d="M20 10.5v3" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/><path d="M6.5 13.5h2.5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>`,
      clear: `<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m7 7 10 10M17 7 7 17" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"/><circle cx="12" cy="12" r="8.5" fill="none" stroke="currentColor" stroke-width="1.8"/></svg>`
    };
    let state = loadState();
    let viewedDate = new Date();
    let selectedGoalId = state.goals[0]?.id ?? null;
    let selectedDateKey = isoDate(new Date());
    let activePage = "tracker";
    let statsView = "monthly";
    let statsGoalIds = [];
    let statsCustomStart = isoDate(new Date(new Date().getFullYear(), new Date().getMonth(), 1));
    let statsCustomEnd = isoDate(new Date());
    let pinMode = "unlock";
    let pinBuffer = "";
    let pinMessage = "";
    let pendingPin = "";

    const goalForm = document.getElementById("goalForm");
    const app = document.getElementById("app");
    const goalList = document.getElementById("goalList");
    const calendar = document.getElementById("calendar");
    const emotionTracker = document.getElementById("emotionTracker");
    const monthTitle = document.getElementById("monthTitle");
    const summary = document.getElementById("summary");
    const detail = document.getElementById("detail");
    const statsDetail = document.getElementById("statsDetail");
    const trackerPage = document.getElementById("trackerPage");
    const statsPage = document.getElementById("statsPage");
    const trackerTab = document.getElementById("trackerTab");
    const statsTab = document.getElementById("statsTab");
    const themeSelect = document.getElementById("themeSelect");
    const passwordButton = document.getElementById("passwordButton");
    const resetButton = document.getElementById("resetButton");
    const pinOverlay = document.getElementById("pinOverlay");
    const goalColor = document.getElementById("goalColor");
    const goalCadence = document.getElementById("goalCadence");
    const customCadence = document.getElementById("customCadence");
    const goalTarget = document.getElementById("goalTarget");
    const goalTargetUnit = document.getElementById("goalTargetUnit");

    document.getElementById("todayLabel").textContent = new Date().toLocaleDateString(undefined, {
      weekday: "long",
      month: "long",
      day: "numeric"
    });

    goalForm.addEventListener("submit", (event) => {
      event.preventDefault();
      const data = new FormData(goalForm);
      const name = String(data.get("goalName")).trim();
      if (!name) return;
      const cadence = normalizedFormCadence(data);
      const goal = {
        id: crypto.randomUUID(),
        name,
        cadence,
        target: targetForCadence(cadence, data),
        color: data.get("goalColor"),
        createdAt: isoDate(new Date()),
        endDate: data.get("goalEndDate") || "",
        completions: [],
        notes: {},
        exceptions: {}
      };
      state.goals.push(goal);
      selectedGoalId = goal.id;
      goalForm.reset();
      setGoalColor(palette[state.goals.length % palette.length]);
      updateCustomCadence();
      saveState();
      render();
    });

    goalCadence.addEventListener("change", updateCustomCadence);
    goalTargetUnit.addEventListener("change", () => {
      updateCustomCadence();
    });

    trackerTab.addEventListener("click", () => switchPage("tracker"));
    statsTab.addEventListener("click", () => switchPage("stats"));
    themeSelect.addEventListener("change", () => {
      state.theme = themeSelect.value;
      applyTheme();
      saveState();
    });
    passwordButton.addEventListener("click", openPasswordSettings);
    resetButton.addEventListener("click", resetTrackerData);

    document.getElementById("prevMonth").addEventListener("click", () => {
      viewedDate = new Date(viewedDate.getFullYear(), viewedDate.getMonth() - 1, 1);
      render();
    });

    document.getElementById("nextMonth").addEventListener("click", () => {
      viewedDate = new Date(viewedDate.getFullYear(), viewedDate.getMonth() + 1, 1);
      render();
    });

    function loadState() {
      const stored = localStorage.getItem(storageKey);
      if (stored) return normalizeState(JSON.parse(stored));
      return {
        theme: "neutral",
        security: { pinHash: "" },
        emotions: {},
        goals: [
          {
            id: crypto.randomUUID(),
            name: "Morning walk",
            cadence: "daily",
            target: 1,
            color: "#287c74",
            createdAt: isoDate(new Date()),
            endDate: "",
            completions: sampleCompletions(0),
            notes: {},
            exceptions: {}
          },
          {
            id: crypto.randomUUID(),
            name: "Deep work",
            cadence: "weekday",
            target: 1,
            color: "#5a66ad",
            createdAt: isoDate(new Date()),
            endDate: "",
            completions: sampleCompletions(2),
            notes: {},
            exceptions: {}
          }
        ]
      };
    }

    function blankState() {
      return {
        theme: "neutral",
        security: { pinHash: "" },
        emotions: {},
        goals: []
      };
    }

    function normalizeState(savedState) {
      return {
        theme: savedState.theme ?? "neutral",
        security: {
          pinHash: savedState.security?.pinHash ?? ""
        },
        emotions: savedState.emotions ?? {},
        goals: (savedState.goals ?? []).map((goal) => ({
          ...goal,
          cadence: goal.cadence ?? "daily",
          target: goal.target ?? defaultTarget(goal.cadence ?? "daily"),
          endDate: goal.endDate ?? "",
          completions: goal.completions ?? [],
          notes: goal.notes ?? {},
          exceptions: goal.exceptions ?? {}
        }))
      };
    }

    function sampleCompletions(offset) {
      const days = [];
      const today = new Date();
      for (let i = 0; i < 24; i++) {
        const date = new Date(today);
        date.setDate(today.getDate() - i);
        if ((i + offset) % 3 !== 1) days.push(isoDate(date));
      }
      return days;
    }

    function saveState() {
      localStorage.setItem(storageKey, JSON.stringify(state));
    }

    function passwordIsEnabled() {
      return Boolean(state.security?.pinHash);
    }

    function passwordSessionKey() {
      return `${storageKey}-pin-unlocked`;
    }

    function passwordIsUnlocked() {
      return !passwordIsEnabled() || sessionStorage.getItem(passwordSessionKey()) === "true";
    }

    async function hashPin(pin) {
      if (!window.crypto?.subtle) return `plain:${pin}`;
      const data = new TextEncoder().encode(`my-simple-tracker:${pin}`);
      const digest = await crypto.subtle.digest("SHA-256", data);
      return [...new Uint8Array(digest)].map((byte) => byte.toString(16).padStart(2, "0")).join("");
    }

    function openPasswordSettings() {
      if (passwordIsEnabled()) {
        openPinModal("manage");
      } else {
        openPinModal("setup");
      }
    }

    function openPinModal(mode, message = "") {
      pinMode = mode;
      pinBuffer = "";
      pinMessage = message;
      if (mode !== "confirm_setup") pendingPin = "";
      pinOverlay.classList.add("visible");
      renderPinModal();
    }

    function closePinModal() {
      if (pinMode === "unlock" && !passwordIsUnlocked()) return;
      pinOverlay.classList.remove("visible");
      pinBuffer = "";
      pinMessage = "";
      pendingPin = "";
    }

    function renderPinModal() {
      const locked = pinMode === "unlock";
      const manage = pinMode === "manage";
      const title = {
        unlock: "Enter Password",
        setup: "Choose Password",
        confirm_setup: "Confirm Password",
        manage: "Password"
      }[pinMode];
      const subtitle = {
        unlock: "Enter your 4 digit code to open My Simple Tracker.",
        setup: "Choose a 4 digit code.",
        confirm_setup: "Enter the same code again.",
        manage: passwordIsEnabled() ? "A 4 digit code is active." : "No password is set."
      }[pinMode];

      pinOverlay.innerHTML = `
        <section class="pin-card">
          <div class="pin-head">
            <div>
              <h2>${title}</h2>
              <div class="pin-subtitle">${subtitle}</div>
            </div>
            ${locked ? "" : '<button class="ghost" id="pinClose" type="button" title="Close">&times;</button>'}
          </div>
          ${manage ? passwordManagementMarkup() : pinEntryMarkup()}
        </section>
      `;

      const close = document.getElementById("pinClose");
      if (close) close.addEventListener("click", closePinModal);

      pinOverlay.querySelectorAll("[data-pin-key]").forEach((button) => {
        button.addEventListener("click", () => handlePinKey(button.dataset.pinKey));
      });
      pinOverlay.querySelectorAll("[data-pin-action]").forEach((button) => {
        button.addEventListener("click", () => handlePinAction(button.dataset.pinAction));
      });
    }

    function passwordManagementMarkup() {
      return `
        <div class="pin-actions">
          <button class="primary" type="button" data-pin-action="change">Change code</button>
          <button class="ghost" type="button" data-pin-action="disable">Disable password</button>
        </div>
        <p class="pin-message">${pinMessage}</p>
      `;
    }

    function pinEntryMarkup() {
      return `
        <div class="pin-dots" aria-label="${pinBuffer.length} of 4 digits entered">
          ${[0, 1, 2, 3].map((index) => `<span class="pin-dot ${index < pinBuffer.length ? "filled" : ""}"></span>`).join("")}
        </div>
        <div class="pin-pad">
          ${["1", "2", "3", "4", "5", "6", "7", "8", "9", "back", "0", "clear"].map((key) => `
            <button class="pin-key" type="button" data-pin-key="${key}">
              ${key === "back" ? "⌫" : key === "clear" ? "Clear" : key}
            </button>
          `).join("")}
        </div>
        <p class="pin-message">${pinMessage}</p>
      `;
    }

    async function handlePinKey(key) {
      if (key === "clear") {
        pinBuffer = "";
        pinMessage = "";
        renderPinModal();
        return;
      }
      if (key === "back") {
        pinBuffer = pinBuffer.slice(0, -1);
        pinMessage = "";
        renderPinModal();
        return;
      }
      if (pinBuffer.length >= 4) return;
      pinBuffer += key;
      pinMessage = "";
      if (pinBuffer.length === 4) {
        await submitPin(pinBuffer);
        return;
      }
      renderPinModal();
    }

    async function submitPin(pin) {
      if (pinMode === "unlock") {
        if (await hashPin(pin) === state.security.pinHash) {
          sessionStorage.setItem(passwordSessionKey(), "true");
          closePinModal();
          render();
        } else {
          openPinModal("unlock", "Wrong code. Try again.");
        }
        return;
      }

      if (pinMode === "setup") {
        pendingPin = pin;
        openPinModal("confirm_setup");
        return;
      }

      if (pinMode === "confirm_setup") {
        if (pin !== pendingPin) {
          openPinModal("setup", "Codes did not match. Start again.");
          return;
        }
        state.security = { pinHash: await hashPin(pin) };
        sessionStorage.setItem(passwordSessionKey(), "true");
        saveState();
        closePinModal();
        render();
      }
    }

    function handlePinAction(action) {
      if (action === "change") {
        openPinModal("setup");
        return;
      }
      if (action === "disable") {
        const confirmed = window.confirm("Disable the password for this tracker?");
        if (!confirmed) return;
        state.security = { pinHash: "" };
        sessionStorage.removeItem(passwordSessionKey());
        saveState();
        closePinModal();
        render();
      }
    }

    function initPasswordGate() {
      if (passwordIsEnabled() && !passwordIsUnlocked()) {
        openPinModal("unlock");
      }
    }

    function resetTrackerData() {
      const confirmed = window.confirm("Are you sure you want to reset all goals, notes, exceptions, moods, and settings?");
      if (!confirmed) return;
      localStorage.removeItem(storageKey);
      sessionStorage.removeItem(passwordSessionKey());
      state = blankState();
      selectedGoalId = null;
      selectedDateKey = isoDate(new Date());
      viewedDate = new Date();
      activePage = "tracker";
      statsView = "monthly";
      statsGoalIds = [];
      statsCustomStart = isoDate(new Date(new Date().getFullYear(), new Date().getMonth(), 1));
      statsCustomEnd = isoDate(new Date());
      saveState();
      render();
    }

    function render() {
      if (!selectedGoalId && state.goals.length) selectedGoalId = state.goals[0].id;
      applyTheme();
      passwordButton.classList.toggle("active", passwordIsEnabled());
      renderPages();
      renderGoals();
      renderSummary();
      renderCalendar();
      renderEmotionTracker();
      renderDetail();
      renderStats();
    }

    function applyTheme() {
      const theme = state.theme ?? "neutral";
      document.body.dataset.theme = theme === "neutral" ? "" : theme;
      themeSelect.value = theme;
    }

    function switchPage(page) {
      activePage = page;
      render();
    }

    function renderPages() {
      const isStats = activePage === "stats";
      app.classList.toggle("stats-mode", isStats);
      trackerPage.classList.toggle("active", !isStats);
      statsPage.classList.toggle("active", isStats);
      trackerTab.classList.toggle("active", !isStats);
      statsTab.classList.toggle("active", isStats);
    }

    function renderGoals() {
      goalList.innerHTML = "";
      if (!state.goals.length) {
        goalList.innerHTML = '<div class="empty">Add your first goal to begin tracking.</div>';
        return;
      }
      state.goals.forEach((goal) => {
        const button = document.createElement("button");
        button.className = `goal-button ${goal.id === selectedGoalId ? "active" : ""}`;
        button.type = "button";
        button.innerHTML = `
          <span class="swatch" style="background:${goal.color}"></span>
          <span>
            <span class="goal-name">${escapeHtml(goal.name)}</span>
            <span class="goal-meta">${cadenceLabel(goal)} · ${goal.completions.length} checks${goal.endDate ? ` · ends ${formatReadableDate(goal.endDate)}` : ""}</span>
          </span>
          <span aria-hidden="true">&#8250;</span>
        `;
        button.addEventListener("click", () => {
          selectedGoalId = goal.id;
          render();
        });
        goalList.appendChild(button);
      });
    }

    function renderSummary() {
      const allDoneToday = state.goals.filter((goal) => goal.completions.includes(isoDate(new Date()))).length;
      const best = state.goals.reduce((winner, goal) => {
        const streak = currentStreak(goal);
        return streak > winner ? streak : winner;
      }, 0);
      const checksThisMonth = state.goals.reduce((sum, goal) => {
        return sum + goal.completions.filter((date) => sameMonth(parseIso(date), viewedDate)).length;
      }, 0);
      const totalChecks = state.goals.reduce((sum, goal) => sum + goal.completions.length, 0);

      summary.innerHTML = [
        statCard(state.goals.length, "Active goals"),
        statCard(allDoneToday, "Completed today"),
        statCard(best, "Best current streak"),
        statCard(checksThisMonth || totalChecks, checksThisMonth ? "Checks this month" : "Total checks")
      ].join("");
    }

    function statCard(value, label) {
      return `<article class="stat"><strong>${value}</strong><span>${label}</span></article>`;
    }

    function renderCalendar() {
      calendar.innerHTML = "";
      const year = viewedDate.getFullYear();
      const month = viewedDate.getMonth();
      monthTitle.textContent = viewedDate.toLocaleDateString(undefined, { month: "long", year: "numeric" });
      const first = new Date(year, month, 1);
      const blanks = (first.getDay() + 6) % 7;
      const daysInMonth = new Date(year, month + 1, 0).getDate();

      for (let i = 0; i < blanks; i++) {
        const blank = document.createElement("div");
        blank.className = "day blank";
        calendar.appendChild(blank);
      }

      for (let day = 1; day <= daysInMonth; day++) {
        const date = new Date(year, month, day);
        const key = isoDate(date);
        const cell = document.createElement("button");
        const endingGoals = state.goals.filter((goal) => goal.endDate === key);
        const emotion = state.emotions?.[key] ?? "";
        cell.className = `day ${key === isoDate(new Date()) ? "today" : ""} ${key === selectedDateKey ? "selected" : ""} ${endingGoals.length ? "end-date" : ""}`;
        if (endingGoals.length === 1) {
          cell.style.setProperty("--end-color", endingGoals[0].color);
        } else if (endingGoals.length > 1) {
          cell.style.setProperty("--end-color", "#252525");
        }
        if (endingGoals.length) {
          cell.title = `Ends: ${endingGoals.map((goal) => goal.name).join(", ")}`;
        }
        cell.type = "button";
        const completedGoals = state.goals.filter((goal) => goal.completions.includes(key));
        const exceptionGoals = state.goals.filter((goal) => goal.exceptions?.[key]);
        cell.innerHTML = `
          <span class="date-number">${day}</span>
          <span class="marks">
            ${completedGoals.map((goal) => `<span class="mark" style="background:${goal.color}" title="${escapeHtml(goal.name)}"></span>`).join("")}
            ${exceptionGoals.map((goal) => `<span class="exception-mark" style="color:${goal.color}" title="${escapeHtml(goal.name)} · ${exceptionLabel(goal.exceptions[key])}"></span>`).join("")}
            ${emotion ? `<span class="emotion-mark" title="${emotionLabel(emotion)}">${emotionIcons[emotion]}</span>` : ""}
          </span>
        `;
        cell.addEventListener("click", () => toggleSelectedGoalOnDate(key));
        calendar.appendChild(cell);
      }
    }

    function renderEmotionTracker() {
      const selectedEmotion = state.emotions?.[selectedDateKey] ?? "";
      emotionTracker.innerHTML = `
        <div class="panel-head">
          <h2>Emotional Status</h2>
          <strong>${formatReadableDate(selectedDateKey)}</strong>
        </div>
        <div class="emotion-buttons">
          ${Object.entries(emotionTypes).map(([value, label]) => `
            <button class="emotion-button ${selectedEmotion === value ? "active" : ""}" type="button" data-emotion="${value}" title="${label}">
              ${emotionIcons[value]}
              <span>${label}</span>
            </button>
          `).join("")}
        </div>
      `;

      emotionTracker.querySelectorAll("[data-emotion]").forEach((button) => {
        button.addEventListener("click", () => {
          saveEmotion(selectedDateKey, button.dataset.emotion);
          saveState();
          render();
        });
      });
    }

    function renderDetail() {
      const goal = selectedGoal();
      if (!goal) {
        detail.innerHTML = '<div class="empty">Choose or add a goal to see details.</div>';
        return;
      }

      const selectedDate = parseIso(selectedDateKey);
      const doneOnSelectedDate = goal.completions.includes(selectedDateKey);
      const monthRate = completionRateForMonth(goal, viewedDate);
      const streak = currentStreak(goal);
      const streakUnit = streakUnitLabel(goal);
      const selectedNote = goal.notes?.[selectedDateKey] ?? "";
      const selectedException = goal.exceptions?.[selectedDateKey] ?? "";
      detail.style.setProperty("--accent", goal.color);
      detail.innerHTML = `
        <div class="selected-banner">
          <div>
            <h2>${escapeHtml(goal.name)}</h2>
            <div class="goal-meta">${cadenceLabel(goal)} · ${goal.completions.length} total checks${goal.endDate ? ` · ends ${formatReadableDate(goal.endDate)}` : ""}</div>
          </div>
          <button class="danger" id="deleteGoal" type="button">Delete</button>
        </div>
        <div class="goal-meta">Editing ${formatReadableDate(selectedDateKey)}</div>
        <button class="check-button ${doneOnSelectedDate ? "done" : ""}" id="toggleSelectedDate" type="button">
          ${doneOnSelectedDate ? "Done" : "Mark complete"}
        </button>
        <div class="field">
          <label for="completionException">Exception</label>
          <select id="completionException">
            <option value="">No exception</option>
            ${Object.entries(exceptionTypes).map(([value, label]) => `<option value="${value}" ${selectedException === value ? "selected" : ""}>${label}</option>`).join("")}
          </select>
        </div>
        <div class="field">
          <label for="completionNote">Note</label>
          <textarea id="completionNote" placeholder="How did it go?">${escapeHtml(selectedNote)}</textarea>
        </div>
        <div>
          <div class="panel-head">
            <h2>Monthly completion</h2>
            <strong>${monthRate}%</strong>
          </div>
          <div class="progress-line"><span style="width:${monthRate}%"></span></div>
        </div>
        <div>
          <div class="panel-head">
            <h2>Last 7 days</h2>
            <strong>${streak} ${streakUnit} streak</strong>
          </div>
          <div class="chart">${weeklyBars(goal)}</div>
        </div>
        <div>
          <div class="panel-head">
            <h2>Recent notes</h2>
          </div>
          ${recentNotes(goal)}
        </div>
      `;

      document.getElementById("toggleSelectedDate").addEventListener("click", () => {
        const note = document.getElementById("completionNote").value.trim();
        toggleCompletion(goal, selectedDateKey, note);
        saveState();
        render();
      });

      document.getElementById("completionException").addEventListener("change", (event) => {
        saveException(goal, selectedDateKey, event.target.value);
        saveState();
        render();
      });

      document.getElementById("completionNote").addEventListener("input", (event) => {
        saveCompletionNote(goal, selectedDateKey, event.target.value);
        saveState();
      });

      document.getElementById("deleteGoal").addEventListener("click", () => {
        state.goals = state.goals.filter((item) => item.id !== goal.id);
        selectedGoalId = state.goals[0]?.id ?? null;
        saveState();
        render();
      });
    }

    function renderStats() {
      if (!state.goals.length) {
        statsDetail.innerHTML = '<section class="panel"><div class="empty">Add goals to see statistics.</div></section>';
        return;
      }

      const goals = selectedStatsGoals();
      const range = statsRange();
      const totalChecks = goals.reduce((sum, goal) => sum + completionsInPeriod(goal, range.start, range.end), 0);
      const totalNotes = goals.reduce((sum, goal) => sum + notesInPeriod(goal, range.start, range.end), 0);
      const totalExceptions = goals.reduce((sum, goal) => sum + exceptionsInPeriod(goal, range.start, range.end), 0);
      const bestGoal = [...goals].sort((a, b) => currentStreak(b) - currentStreak(a))[0];
      const mostActiveGoal = [...goals].sort((a, b) => completionsInPeriod(b, range.start, range.end) - completionsInPeriod(a, range.start, range.end))[0];

      statsDetail.innerHTML = `
        <section class="panel stats-controls">
          <div class="panel-head">
            <h2>Statistics</h2>
            <strong>${range.label}</strong>
          </div>
          <div class="control-row">
            <div class="segmented">
              ${["daily", "weekly", "monthly", "yearly", "custom"].map((view) => `
                <button class="segment ${statsView === view ? "active" : ""}" type="button" data-stats-view="${view}">
                  ${capitalize(view)}
                </button>
              `).join("")}
            </div>
          </div>
          <div class="custom-range ${statsView === "custom" ? "visible" : ""}">
            <div class="field">
              <label for="statsCustomStart">From</label>
              <input id="statsCustomStart" type="date" value="${statsCustomStart}">
            </div>
            <div class="field">
              <label for="statsCustomEnd">To</label>
              <input id="statsCustomEnd" type="date" value="${statsCustomEnd}">
            </div>
          </div>
          <div class="field">
            <label>Goals</label>
            <div class="goal-filter">
              <button class="goal-chip ${statsGoalIds.length === 0 ? "active" : ""}" type="button" data-goal-filter="all">All</button>
              ${state.goals.map((goal) => `
                <button class="goal-chip ${statsGoalIds.includes(goal.id) ? "active" : ""}" style="--chip-color:${goal.color}" type="button" data-goal-filter="${goal.id}">
                  <span class="mark" style="background:${goal.color}"></span>${escapeHtml(goal.name)}
                </button>
              `).join("")}
            </div>
          </div>
        </section>

        <div class="stats-stack">
          <section class="panel">
            <div class="panel-head">
              <h2>Completion Trend</h2>
              <strong>${totalChecks} checks</strong>
            </div>
            <div class="wide-chart" style="grid-template-columns: repeat(${statsBuckets().length}, minmax(0, 1fr))">${trendBars(goals)}</div>
          </section>

          <section class="panel">
            <div class="panel-head">
              <h2>Goal Completion</h2>
              <strong>${goals.length} shown</strong>
            </div>
            ${goalCompletionBars(goals, range)}
          </section>

          <section class="panel">
            <div class="panel-head">
              <h2>Checks By Goal</h2>
              <strong>${totalChecks}</strong>
            </div>
            ${goalPie(goals, range)}
          </section>
        </div>

        <div class="stats-stack">
          <section class="panel">
            <div class="panel-head">
              <h2>Highlights</h2>
            </div>
            <div class="mini-list">
              ${miniRow(bestGoal.color, "Best streak", `${bestGoal.name} · ${currentStreak(bestGoal)} ${streakUnitLabel(bestGoal)}`)}
              ${miniRow(mostActiveGoal.color, "Most checks", `${mostActiveGoal.name} · ${completionsInPeriod(mostActiveGoal, range.start, range.end)}`)}
              ${miniRow("#d79d22", "Notes written", String(totalNotes))}
              ${miniRow("#c85d45", "Exceptions", String(totalExceptions))}
              ${miniRow("#666a73", "Tracked goals", String(goals.length))}
            </div>
          </section>

          <section class="panel">
            <div class="panel-head">
              <h2>Cadence Mix</h2>
            </div>
            ${cadenceMix(goals)}
          </section>

          <section class="panel">
            <div class="panel-head">
              <h2>Emotional Status</h2>
              <strong>${emotionCount(range)}</strong>
            </div>
            ${emotionPie(range)}
          </section>

          <section class="panel">
            <div class="panel-head">
              <h2>Exceptions</h2>
              <strong>${totalExceptions}</strong>
            </div>
            ${exceptionBreakdown(goals, range)}
          </section>
        </div>
      `;

      bindStatsControls();
    }

    function weeklyBars(goal) {
      const today = new Date();
      return Array.from({ length: 7 }, (_, index) => {
        const date = new Date(today);
        date.setDate(today.getDate() - (6 - index));
        const key = isoDate(date);
        const done = goal.completions.includes(key);
        return `
          <div class="bar-wrap">
            <div class="bar-track"><div class="bar" style="height:${done ? 100 : 8}%"></div></div>
            <div class="bar-label">${date.toLocaleDateString(undefined, { weekday: "short" }).slice(0, 2)}</div>
          </div>
        `;
      }).join("");
    }

    function bindStatsControls() {
      statsDetail.querySelectorAll("[data-stats-view]").forEach((button) => {
        button.addEventListener("click", () => {
          statsView = button.dataset.statsView;
          render();
        });
      });

      statsDetail.querySelectorAll("[data-goal-filter]").forEach((button) => {
        button.addEventListener("click", () => {
          const id = button.dataset.goalFilter;
          if (id === "all") {
            statsGoalIds = [];
          } else if (statsGoalIds.includes(id)) {
            statsGoalIds = statsGoalIds.filter((goalId) => goalId !== id);
          } else {
            statsGoalIds.push(id);
          }
          render();
        });
      });

      const startInput = document.getElementById("statsCustomStart");
      const endInput = document.getElementById("statsCustomEnd");
      if (startInput && endInput) {
        startInput.addEventListener("change", () => {
          statsCustomStart = startInput.value || statsCustomStart;
          render();
        });
        endInput.addEventListener("change", () => {
          statsCustomEnd = endInput.value || statsCustomEnd;
          render();
        });
      }
    }

    function selectedStatsGoals() {
      const selected = statsGoalIds.length
        ? state.goals.filter((goal) => statsGoalIds.includes(goal.id))
        : state.goals;
      return selected.length ? selected : state.goals;
    }

    function statsRange() {
      const today = new Date();
      if (statsView === "daily") {
        const start = new Date(today);
        start.setDate(today.getDate() - 13);
        return { start: dayStart(start), end: dayEnd(today), label: "Last 14 days" };
      }
      if (statsView === "weekly") {
        const start = weekStart(today);
        start.setDate(start.getDate() - 77);
        return { start, end: weekEnd(today), label: "Last 12 weeks" };
      }
      if (statsView === "yearly") {
        const start = new Date(today.getFullYear() - 4, 0, 1);
        return { start, end: new Date(today.getFullYear(), 11, 31, 23, 59, 59, 999), label: "Last 5 years" };
      }
      if (statsView === "custom") {
        const start = dayStart(parseIso(statsCustomStart));
        const end = dayEnd(parseIso(statsCustomEnd));
        if (start > end) return { start: end, end: dayEnd(start), label: "Custom range" };
        return { start, end, label: `${formatReadableDate(statsCustomStart)} - ${formatReadableDate(statsCustomEnd)}` };
      }
      const start = new Date(today.getFullYear(), today.getMonth() - 11, 1);
      return { start, end: monthEnd(today), label: "Last 12 months" };
    }

    function statsBuckets() {
      const range = statsRange();
      const buckets = [];
      if (statsView === "daily" || statsView === "custom") {
        const cursor = dayStart(range.start);
        while (cursor <= range.end && buckets.length < 32) {
          buckets.push({
            start: dayStart(cursor),
            end: dayEnd(cursor),
            label: cursor.toLocaleDateString(undefined, { month: "short", day: "numeric" })
          });
          cursor.setDate(cursor.getDate() + 1);
        }
        return buckets;
      }
      if (statsView === "weekly") {
        const cursor = weekStart(range.start);
        while (cursor <= range.end) {
          buckets.push({
            start: new Date(cursor),
            end: weekEnd(cursor),
            label: `${cursor.toLocaleDateString(undefined, { month: "short", day: "numeric" })}`
          });
          cursor.setDate(cursor.getDate() + 7);
        }
        return buckets;
      }
      if (statsView === "yearly") {
        for (let year = range.start.getFullYear(); year <= range.end.getFullYear(); year++) {
          buckets.push({
            start: new Date(year, 0, 1),
            end: new Date(year, 11, 31, 23, 59, 59, 999),
            label: String(year)
          });
        }
        return buckets;
      }
      const cursor = new Date(range.start);
      while (cursor <= range.end) {
        buckets.push({
          start: monthStart(cursor),
          end: monthEnd(cursor),
          label: cursor.toLocaleDateString(undefined, { month: "short" })
        });
        cursor.setMonth(cursor.getMonth() + 1);
      }
      return buckets;
    }

    function trendBars(goals) {
      const buckets = statsBuckets();
      const items = buckets.map((bucket) => ({
        ...bucket,
        count: goals.reduce((sum, goal) => sum + completionsInPeriod(goal, bucket.start, bucket.end), 0)
      }));
      const max = Math.max(1, ...items.map((item) => item.count));

      return items.map((item) => `
        <div class="bar-wrap">
          <div class="bar-track"><div class="bar" style="height:${Math.max(4, Math.round((item.count / max) * 100))}%"></div></div>
          <div class="bar-label">${escapeHtml(item.label)}</div>
        </div>
      `).join("");
    }

    function goalCompletionBars(goals, range) {
      if (!goals.length) {
        return '<div class="empty">No goals yet.</div>';
      }
      return `
        <div class="goal-bars">
          ${goals.map((goal) => {
            const rate = completionRateForRange(goal, range.start, range.end);
            return `
              <div class="goal-bar-row">
                <span class="goal-bar-label">${escapeHtml(goal.name)}</span>
                <span class="goal-bar-track"><span class="goal-bar-fill" style="width:${rate}%; background:${goal.color}"></span></span>
                <span class="goal-bar-value">${rate}%</span>
              </div>
            `;
          }).join("")}
        </div>
      `;
    }

    function cadenceMix(goals) {
      const counts = goals.reduce((items, goal) => {
        const label = cadenceLabel(goal);
        items[label] = (items[label] ?? 0) + 1;
        return items;
      }, {});
      const max = Math.max(1, ...Object.values(counts));

      return `
        <div class="goal-bars">
          ${Object.entries(counts).map(([label, count]) => `
            <div class="goal-bar-row">
              <span class="goal-bar-label">${escapeHtml(label)}</span>
              <span class="goal-bar-track"><span class="goal-bar-fill" style="width:${Math.round((count / max) * 100)}%; background:#5a66ad"></span></span>
              <span class="goal-bar-value">${count}</span>
            </div>
          `).join("")}
        </div>
      `;
    }

    function goalPie(goals, range) {
      const slices = goals
        .map((goal) => ({
          label: goal.name,
          color: goal.color,
          value: completionsInPeriod(goal, range.start, range.end)
        }))
        .filter((item) => item.value > 0);
      return pieChart(slices, "No checks in this range.");
    }

    function emotionPie(range) {
      const slices = Object.entries(emotionTypes).map(([value, label], index) => ({
        label,
        color: ["#287c74", "#6d9f71", "#d79d22", "#7a4f95", "#c85d45", "#666a73"][index],
        value: Object.entries(state.emotions ?? {}).filter(([date, emotion]) => {
          const parsed = parseIso(date);
          return emotion === value && parsed >= range.start && parsed <= range.end;
        }).length
      })).filter((item) => item.value > 0);
      return pieChart(slices, "No emotional status recorded in this range.");
    }

    function exceptionBreakdown(goals, range) {
      const counts = Object.fromEntries(Object.keys(exceptionTypes).map((key) => [key, 0]));
      goals.forEach((goal) => {
        Object.entries(goal.exceptions ?? {}).forEach(([date, exception]) => {
          const parsed = parseIso(date);
          if (parsed >= range.start && parsed <= range.end && counts[exception] !== undefined) {
            counts[exception] += 1;
          }
        });
      });
      const max = Math.max(1, ...Object.values(counts));
      if (!Object.values(counts).some(Boolean)) return '<div class="empty">No exceptions in this range.</div>';
      return `
        <div class="goal-bars">
          ${Object.entries(counts).filter(([, count]) => count > 0).map(([key, count]) => `
            <div class="goal-bar-row">
              <span class="goal-bar-label">${exceptionLabel(key)}</span>
              <span class="goal-bar-track"><span class="goal-bar-fill" style="width:${Math.round((count / max) * 100)}%; background:#c85d45"></span></span>
              <span class="goal-bar-value">${count}</span>
            </div>
          `).join("")}
        </div>
      `;
    }

    function pieChart(slices, emptyText) {
      if (!slices.length) return `<div class="empty">${emptyText}</div>`;
      const total = slices.reduce((sum, slice) => sum + slice.value, 0);
      let cursor = 0;
      const gradient = slices.map((slice) => {
        const start = cursor;
        cursor += (slice.value / total) * 100;
        return `${slice.color} ${start}% ${cursor}%`;
      }).join(", ");
      return `
        <div class="pie-wrap">
          <div class="pie" style="background: conic-gradient(${gradient})"></div>
          <div class="legend">
            ${slices.map((slice) => `
              <div class="legend-row">
                <span class="legend-dot" style="background:${slice.color}"></span>
                <span class="goal-bar-label">${escapeHtml(slice.label)}</span>
                <strong>${slice.value}</strong>
              </div>
            `).join("")}
          </div>
        </div>
      `;
    }

    function emotionCount(range) {
      return Object.keys(state.emotions ?? {}).filter((date) => {
        const parsed = parseIso(date);
        return parsed >= range.start && parsed <= range.end;
      }).length;
    }

    function miniRow(color, label, value) {
      return `
        <div class="mini-row">
          <span class="mark" style="background:${color}"></span>
          <span class="goal-bar-label">${escapeHtml(label)}</span>
          <strong class="goal-bar-value">${escapeHtml(value)}</strong>
        </div>
      `;
    }

    function recentNotes(goal) {
      const notes = [...goal.completions]
        .filter((date) => goal.notes?.[date])
        .sort()
        .reverse()
        .slice(0, 5);

      if (!notes.length) {
        return '<div class="empty">No notes yet.</div>';
      }

      return `
        <div class="note-list">
          ${notes.map((date) => `
            <article class="note-item">
              <strong class="note-date">${formatReadableDate(date)}</strong>
              <p class="note-text">${escapeHtml(goal.notes[date])}</p>
            </article>
          `).join("")}
        </div>
      `;
    }

    function toggleSelectedGoalOnDate(key) {
      selectedDateKey = key;
      render();
    }

    function toggleCompletion(goal, key, note = "") {
      if (goal.completions.includes(key)) {
        goal.completions = goal.completions.filter((date) => date !== key);
        if (goal.notes) delete goal.notes[key];
      } else {
        clearException(goal, key);
        goal.completions.push(key);
        goal.completions.sort();
        saveCompletionNote(goal, key, note);
      }
    }

    function saveException(goal, key, exception) {
      goal.exceptions = goal.exceptions ?? {};
      goal.completions = goal.completions.filter((date) => date !== key);
      if (goal.notes) delete goal.notes[key];
      if (exception) {
        goal.exceptions[key] = exception;
      } else {
        delete goal.exceptions[key];
      }
    }

    function clearException(goal, key) {
      if (goal.exceptions) delete goal.exceptions[key];
    }

    function saveCompletionNote(goal, key, note) {
      goal.notes = goal.notes ?? {};
      const cleanNote = String(note).trim();
      if (cleanNote) {
        goal.notes[key] = cleanNote;
      } else {
        delete goal.notes[key];
      }
    }

    function saveEmotion(key, emotion) {
      state.emotions = state.emotions ?? {};
      if (emotion) {
        state.emotions[key] = emotion;
      } else {
        delete state.emotions[key];
      }
    }

    function selectedGoal() {
      return state.goals.find((goal) => goal.id === selectedGoalId);
    }

    function currentStreak(goal) {
      if (goal.cadence === "weekly" || goal.cadence === "custom_weekly") {
        return periodStreak(goal, "week");
      }
      if (goal.cadence === "custom_monthly") {
        return periodStreak(goal, "month");
      }
      return dailyStreak(goal);
    }

    function completionRateForMonth(goal, date) {
      if (goal.cadence === "custom_monthly") {
        if (!activeDaysInPeriod(goal, monthStart(date), monthEnd(date))) return 0;
        const complete = completionsInPeriod(goal, monthStart(date), monthEnd(date));
        const target = adjustedTargetForPeriod(goal, monthStart(date), monthEnd(date));
        return target ? Math.min(100, Math.round((complete / target) * 100)) : 100;
      }
      if (goal.cadence === "weekly" || goal.cadence === "custom_weekly") {
        const weeks = weeksTouchingMonth(date);
        const activeWeeks = weeks.filter(([start, end]) => activeDaysInPeriod(goal, start, end) > 0);
        const completeWeeks = activeWeeks.filter(([start, end]) => periodIsComplete(goal, start, end)).length;
        return activeWeeks.length ? Math.round((completeWeeks / activeWeeks.length) * 100) : 0;
      }

      const year = date.getFullYear();
      const month = date.getMonth();
      const daysInMonth = new Date(year, month + 1, 0).getDate();
      let expected = 0;
      let complete = 0;
      for (let day = 1; day <= daysInMonth; day++) {
        const cursor = new Date(year, month, day);
        if (!isExpectedDay(goal, cursor)) continue;
        expected += 1;
        if (goal.completions.includes(isoDate(cursor))) complete += 1;
      }
      return expected ? Math.round((complete / expected) * 100) : 0;
    }

    function isExpectedDay(goal, date) {
      if (!goalIsActiveOnDate(goal, date)) return false;
      if (goal.exceptions?.[isoDate(date)]) return false;
      if (goal.cadence === "custom_weekly" || goal.cadence === "custom_monthly") return true;
      if (goal.cadence === "weekday") return date.getDay() >= 1 && date.getDay() <= 5;
      if (goal.cadence === "weekly") return date.getDay() === 1;
      return true;
    }

    function goalIsActiveOnDate(goal, date) {
      const key = isoDate(date);
      if (goal.createdAt && key < goal.createdAt) return false;
      if (goal.endDate && key > goal.endDate) return false;
      return true;
    }

    function dailyStreak(goal) {
      let streak = 0;
      const cursor = new Date();
      for (let i = 0; i < 365; i++) {
        if (!isExpectedDay(goal, cursor)) {
          cursor.setDate(cursor.getDate() - 1);
          continue;
        }
        const key = isoDate(cursor);
        if (goal.completions.includes(key)) {
          streak += 1;
          cursor.setDate(cursor.getDate() - 1);
          continue;
        }
        return streak;
      }
      return streak;
    }

    function periodStreak(goal, unit) {
      let streak = 0;
      let cursor = new Date();
      let isCurrentPeriod = true;
      for (let i = 0; i < 120; i++) {
        const start = unit === "month" ? monthStart(cursor) : weekStart(cursor);
        const end = unit === "month" ? monthEnd(cursor) : weekEnd(cursor);
        if (!activeDaysInPeriod(goal, start, end)) {
          if (isCurrentPeriod) {
            cursor = new Date(start);
            cursor.setDate(cursor.getDate() - 1);
            isCurrentPeriod = false;
            continue;
          }
          return streak;
        }
        const complete = periodIsComplete(goal, start, end);
        if (complete) {
          streak += 1;
          cursor = new Date(start);
          cursor.setDate(cursor.getDate() - 1);
          isCurrentPeriod = false;
          continue;
        }
        if (isCurrentPeriod) {
          cursor = new Date(start);
          cursor.setDate(cursor.getDate() - 1);
          isCurrentPeriod = false;
          continue;
        }
        return streak;
      }
      return streak;
    }

    function completionsInPeriod(goal, start, end) {
      return goal.completions.filter((value) => {
        const date = parseIso(value);
        return date >= start && date <= end;
      }).length;
    }

    function notesInPeriod(goal, start, end) {
      return Object.keys(goal.notes ?? {}).filter((value) => {
        const date = parseIso(value);
        return date >= start && date <= end;
      }).length;
    }

    function exceptionsInPeriod(goal, start, end) {
      return Object.keys(goal.exceptions ?? {}).filter((value) => {
        const date = parseIso(value);
        return date >= start && date <= end && goalIsActiveOnDate(goal, date);
      }).length;
    }

    function adjustedTargetForPeriod(goal, start, end) {
      if (!activeDaysInPeriod(goal, start, end)) return 0;
      return Math.max(0, goal.target - exceptionsInPeriod(goal, start, end));
    }

    function activeDaysInPeriod(goal, start, end) {
      let count = 0;
      const cursor = new Date(start);
      while (cursor <= end) {
        if (goalIsActiveOnDate(goal, cursor)) count += 1;
        cursor.setDate(cursor.getDate() + 1);
      }
      return count;
    }

    function periodIsComplete(goal, start, end) {
      if (!activeDaysInPeriod(goal, start, end)) return false;
      const target = adjustedTargetForPeriod(goal, start, end);
      return target === 0 || completionsInPeriod(goal, start, end) >= target;
    }

    function completionRateForRange(goal, start, end) {
      if (goal.cadence === "weekly" || goal.cadence === "custom_weekly") {
        const weeks = periodsTouchingRange(start, end, "week");
        const activeWeeks = weeks.filter(([periodStart, periodEnd]) => activeDaysInPeriod(goal, periodStart, periodEnd) > 0);
        const completeWeeks = activeWeeks.filter(([periodStart, periodEnd]) => periodIsComplete(goal, periodStart, periodEnd)).length;
        return activeWeeks.length ? Math.round((completeWeeks / activeWeeks.length) * 100) : 0;
      }

      if (goal.cadence === "custom_monthly") {
        const months = periodsTouchingRange(start, end, "month");
        const activeMonths = months.filter(([periodStart, periodEnd]) => activeDaysInPeriod(goal, periodStart, periodEnd) > 0);
        const completeMonths = activeMonths.filter(([periodStart, periodEnd]) => periodIsComplete(goal, periodStart, periodEnd)).length;
        return activeMonths.length ? Math.round((completeMonths / activeMonths.length) * 100) : 0;
      }

      let expected = 0;
      let complete = 0;
      const cursor = dayStart(start);
      while (cursor <= end) {
        if (isExpectedDay(goal, cursor)) {
          expected += 1;
          if (goal.completions.includes(isoDate(cursor))) complete += 1;
        }
        cursor.setDate(cursor.getDate() + 1);
      }
      return expected ? Math.round((complete / expected) * 100) : 0;
    }

    function weekStart(date) {
      const start = new Date(date);
      start.setHours(0, 0, 0, 0);
      start.setDate(start.getDate() - ((start.getDay() + 6) % 7));
      return start;
    }

    function weekEnd(date) {
      const end = weekStart(date);
      end.setDate(end.getDate() + 6);
      end.setHours(23, 59, 59, 999);
      return end;
    }

    function monthStart(date) {
      return new Date(date.getFullYear(), date.getMonth(), 1);
    }

    function monthEnd(date) {
      return new Date(date.getFullYear(), date.getMonth() + 1, 0, 23, 59, 59, 999);
    }

    function dayStart(date) {
      const start = new Date(date);
      start.setHours(0, 0, 0, 0);
      return start;
    }

    function dayEnd(date) {
      const end = new Date(date);
      end.setHours(23, 59, 59, 999);
      return end;
    }

    function periodsTouchingRange(start, end, unit) {
      const periods = [];
      let cursor = unit === "month" ? monthStart(start) : weekStart(start);
      while (cursor <= end) {
        const periodStart = new Date(cursor);
        const periodEnd = unit === "month" ? monthEnd(cursor) : weekEnd(cursor);
        periods.push([periodStart, periodEnd]);
        if (unit === "month") {
          cursor.setMonth(cursor.getMonth() + 1);
        } else {
          cursor.setDate(cursor.getDate() + 7);
        }
      }
      return periods;
    }

    function weeksTouchingMonth(date) {
      const weeks = [];
      const monthStartDate = monthStart(date);
      const monthEndDate = monthEnd(date);
      let cursor = weekStart(monthStartDate);
      while (cursor <= monthEndDate) {
        const start = new Date(cursor);
        const end = weekEnd(start);
        weeks.push([start, end]);
        cursor.setDate(cursor.getDate() + 7);
      }
      return weeks;
    }

    function cadenceLabel(goal) {
      if (goal.cadence === "weekday") return "Weekdays";
      if (goal.cadence === "weekly") return "1 time per week";
      if (goal.cadence === "custom_weekly") return `${goal.target} times per week`;
      if (goal.cadence === "custom_monthly") return `${goal.target} times per month`;
      return "Daily";
    }

    function streakUnitLabel(goal) {
      if (goal.cadence === "weekly" || goal.cadence === "custom_weekly") return "week";
      if (goal.cadence === "custom_monthly") return "month";
      return "day";
    }

    function exceptionLabel(value) {
      return exceptionTypes[value] ?? "Exception";
    }

    function emotionLabel(value) {
      return emotionTypes[value] ?? "Emotional status";
    }

    function normalizedFormCadence(data) {
      const cadence = data.get("goalCadence");
      if (cadence === "custom") {
        return data.get("goalTargetUnit") === "month" ? "custom_monthly" : "custom_weekly";
      }
      return cadence;
    }

    function targetForCadence(cadence, data) {
      if (cadence === "custom_weekly" || cadence === "custom_monthly") {
        return Math.max(1, Number(data.get("goalTarget")) || 1);
      }
      return defaultTarget(cadence);
    }

    function defaultTarget(cadence) {
      return cadence === "weekly" ? 1 : 1;
    }

    function updateCustomCadence() {
      const isCustom = goalCadence.value === "custom";
      customCadence.classList.toggle("visible", isCustom);
      goalTarget.max = goalTargetUnit.value === "month" ? "31" : "7";
      if (Number(goalTarget.value) > Number(goalTarget.max)) goalTarget.value = goalTarget.max;
    }

    function sameMonth(a, b) {
      return a.getFullYear() === b.getFullYear() && a.getMonth() === b.getMonth();
    }

    function isoDate(date) {
      const copy = new Date(date);
      copy.setHours(12, 0, 0, 0);
      return copy.toISOString().slice(0, 10);
    }

    function parseIso(value) {
      const [year, month, day] = value.split("-").map(Number);
      return new Date(year, month - 1, day);
    }

    function formatReadableDate(value) {
      return parseIso(value).toLocaleDateString(undefined, {
        month: "short",
        day: "numeric",
        year: "numeric"
      });
    }

    function capitalize(value) {
      return String(value).charAt(0).toUpperCase() + String(value).slice(1);
    }

    function escapeHtml(value) {
      return String(value).replace(/[&<>"']/g, (char) => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#039;"
      })[char]);
    }

    function setGoalColor(value) {
      goalColor.value = value;
    }

    setGoalColor(palette[state.goals.length % palette.length]);
    updateCustomCadence();
    render();
    initPasswordGate();
  </script>
</body>
</html>
"""


class GoalTrackerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path not in ("/", "/index.html"):
            self.send_error(404)
            return
        body = APP_HTML.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        return


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True


if __name__ == "__main__":
    host = "127.0.0.1"
    port = 8787
    url = f"http://{host}:{port}"
    try:
        server = ThreadedHTTPServer((host, port), GoalTrackerHandler)
    except SocketError:
        print(f"Goal Progress Tracker appears to already be running at {url}")
        webbrowser.open(url)
        raise SystemExit(0)
    print(f"Goal Progress Tracker running at {url}")
    webbrowser.open(url)
    server.serve_forever()
