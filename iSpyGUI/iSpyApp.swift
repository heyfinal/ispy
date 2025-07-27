import SwiftUI
import Combine

@main
struct iSpyApp: App {
    @StateObject private var deviceManager = DeviceManager()
    @StateObject private var diagnosticsManager = DiagnosticsManager()
    @StateObject private var aiManager = AIManager()
    @StateObject private var themeManager = ThemeManager()
    
    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(deviceManager)
                .environmentObject(diagnosticsManager)
                .environmentObject(aiManager)
                .environmentObject(themeManager)
                .preferredColorScheme(.dark)
                .onAppear {
                    setupAppearance()
                }
        }
        .windowStyle(.hiddenTitleBar)
        .windowResizability(.contentSize)
    }
    
    private func setupAppearance() {
        // Configure window appearance
        if let window = NSApplication.shared.windows.first {
            window.titlebarAppearsTransparent = true
            window.isMovableByWindowBackground = true
            window.backgroundColor = NSColor.clear
        }
    }
}

// MARK: - Theme Manager
class ThemeManager: ObservableObject {
    @Published var currentTheme: Theme = .dark
    
    enum Theme {
        case dark
        case light
        
        var primaryColor: Color {
            switch self {
            case .dark: return Color(red: 0.1, green: 0.1, blue: 0.15)
            case .light: return Color.white
            }
        }
        
        var secondaryColor: Color {
            switch self {
            case .dark: return Color(red: 0.15, green: 0.15, blue: 0.2)
            case .light: return Color(red: 0.95, green: 0.95, blue: 0.97)
            }
        }
        
        var accentColor: Color {
            return Color(red: 0.0, green: 0.8, blue: 1.0) // Bright cyan
        }
        
        var textPrimary: Color {
            switch self {
            case .dark: return Color.white
            case .light: return Color.black
            }
        }
        
        var textSecondary: Color {
            switch self {
            case .dark: return Color(white: 0.7)
            case .light: return Color(white: 0.3)
            }
        }
    }
}