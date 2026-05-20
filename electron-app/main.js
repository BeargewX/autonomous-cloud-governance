const { app, BrowserWindow } = require('electron')
const path = require('path')
const fs = require('fs')

let mainWindow

function createWindow() {
  const iconPath = path.join(__dirname, 'assets/icon.png')
  const windowOptions = {
    width: 1200,
    height: 800,
    minWidth: 900,
    minHeight: 600,
    titleBarStyle: 'hiddenInset',
    backgroundColor: '#0f1117',
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      webSecurity: true,
      preload: path.join(__dirname, 'preload.js')
    }
  }

  if (fs.existsSync(iconPath)) {
    windowOptions.icon = iconPath
  }

  mainWindow = new BrowserWindow(windowOptions)
  mainWindow.loadFile('index.html')
  mainWindow.setTitle('Cloud Governance Monitor')
}

app.whenReady().then(createWindow)

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit()
})

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) createWindow()
})
