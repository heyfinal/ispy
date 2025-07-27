# iSpy SwiftUI GUI

🎨 **Elegant, cutting-edge SwiftUI interface for the iSpy iOS diagnostic toolkit**

## Screenshots

*Note: Add screenshots here after building*

## Features

### 🌙 **Dark Mode Design**
- Pure dark aesthetic with bright cyan accents
- Glassmorphism effects and subtle shadows
- Custom borderless window design
- Smooth animations throughout

### 📊 **Dashboard**
- Real-time device health overview
- Interactive diagnostic module cards
- Health score visualization
- Recent activity feed

### 📱 **Device Management** 
- Auto-discovery of connected iOS devices
- Device cards with battery/storage indicators
- Connection status monitoring
- Detailed device information

### 🧠 **AI Assistant**
- ChatGPT-style interface
- Quick action suggestions
- Contextual device troubleshooting
- Real-time conversation flow

### 📈 **Analytics**
- Interactive trend charts
- Time range selection (24H, 7D, 30D, 1Y)
- Data export options (PDF, CSV, JSON)
- Predictive insights

### ⚙️ **Settings**
- AI configuration and API key management
- Diagnostic preferences
- Notification settings
- Data privacy controls

## Architecture

### **SwiftUI Views:**
- `ContentView.swift` - Main navigation and layout
- `DashboardView.swift` - Health overview and diagnostics
- `DevicesView.swift` - Device discovery and management
- `AIAssistantView.swift` - Chat interface
- `AnalyticsView.swift` - Data visualization
- `SettingsView.swift` - App configuration
- `DeviceDetailView.swift` - Detailed device information

### **Data Models:**
- `DeviceManager.swift` - Device state and operations
- `DiagnosticsManager.swift` - Diagnostic data and processing
- `ThemeManager.swift` - UI theming and colors

### **Integration:**
- Connects to Python backend via shell commands
- Real-time data updates
- Async/await pattern for operations
- ObservableObject state management

## Requirements

- **macOS 14.0+** (Sonoma or later)
- **Xcode 15.0+**
- **Swift 5.9+**
- **Python backend** (ispy.py)

## Building

1. **Open in Xcode:**
```bash
cd iSpyGUI
open iSpy.xcodeproj
```

2. **Build and Run:**
- Select your Mac as target
- Press `Cmd + R` to build and run
- Or `Cmd + B` to build only

3. **Create Distribution:**
- `Product > Archive`
- `Distribute App > Copy App`

## Python Integration

The SwiftUI app communicates with the Python backend:

```swift
// Example integration
let pythonInterface = PythonInterface()
pythonInterface.getConnectedDevices { devices in
    DispatchQueue.main.async {
        self.devices = devices
    }
}
```

## Customization

### **Theme Colors:**
```swift
// In ThemeManager.swift
var accentColor: Color {
    return Color(red: 0.0, green: 0.8, blue: 1.0) // Bright cyan
}
```

### **Add New Diagnostic Modules:**
```swift
// In DiagnosticsManager.swift
DiagnosticModule(
    name: "Custom Module",
    description: "Your custom diagnostic",
    icon: "custom.icon",
    status: .good,
    score: 85.0
)
```

## Performance

- **Lazy Loading** for large data sets
- **Efficient Rendering** with SwiftUI best practices
- **Memory Management** with proper cleanup
- **60fps Animations** throughout the interface

## Future Enhancements

- [ ] **Live Charts** with real-time updates
- [ ] **Drag & Drop** file operations
- [ ] **Multi-device** management
- [ ] **Plugin System** for custom modules
- [ ] **Export Templates** for reports
- [ ] **Notification Center** integration

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## License

MIT License - see [LICENSE](../LICENSE) for details.

---

**iSpy SwiftUI GUI - Where elegant design meets powerful diagnostics** ✨