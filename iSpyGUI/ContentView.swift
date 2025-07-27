import SwiftUI

struct ContentView: View {
    @EnvironmentObject var deviceManager: DeviceManager
    @EnvironmentObject var themeManager: ThemeManager
    @State private var selectedTab: Tab = .dashboard
    @State private var showingSplash = true
    
    enum Tab: CaseIterable {
        case dashboard, devices, analytics, ai, settings
        
        var icon: String {
            switch self {
            case .dashboard: return "rectangle.grid.3x2"
            case .devices: return "iphone"
            case .analytics: return "chart.line.uptrend.xyaxis"
            case .ai: return "brain.head.profile"
            case .settings: return "gear"
            }
        }
        
        var title: String {
            switch self {
            case .dashboard: return "Dashboard"
            case .devices: return "Devices"
            case .analytics: return "Analytics"
            case .ai: return "AI Assistant"
            case .settings: return "Settings"
            }
        }
    }
    
    var body: some View {
        ZStack {
            if showingSplash {
                SplashView()
                    .transition(.opacity)
                    .onAppear {
                        DispatchQueue.main.asyncAfter(deadline: .now() + 2) {
                            withAnimation(.easeInOut(duration: 0.8)) {
                                showingSplash = false
                            }
                        }
                    }
            } else {
                mainInterface
                    .transition(.opacity)
            }
        }
        .background(themeManager.currentTheme.primaryColor.ignoresSafeArea())
    }
    
    var mainInterface: some View {
        HStack(spacing: 0) {
            // Sidebar
            VStack(spacing: 0) {
                // Logo and Title
                VStack(spacing: 8) {
                    Image(systemName: "eye.circle.fill")
                        .font(.system(size: 32, weight: .bold))
                        .foregroundColor(themeManager.currentTheme.accentColor)
                    
                    Text("iSpy")
                        .font(.title2)
                        .fontWeight(.bold)
                        .foregroundColor(themeManager.currentTheme.textPrimary)
                }
                .padding(.top, 24)
                .padding(.bottom, 32)
                
                // Navigation Tabs
                VStack(spacing: 8) {
                    ForEach(Tab.allCases, id: \.self) { tab in
                        NavigationButton(
                            tab: tab,
                            isSelected: selectedTab == tab
                        ) {
                            withAnimation(.spring(response: 0.3, dampingFraction: 0.8)) {
                                selectedTab = tab
                            }
                        }
                    }
                }
                
                Spacer()
                
                // Connection Status
                ConnectionStatusView()
                    .padding(.bottom, 24)
            }
            .frame(width: 240)
            .background(themeManager.currentTheme.secondaryColor)
            
            // Main Content Area
            VStack(spacing: 0) {
                // Custom Title Bar
                CustomTitleBar()
                
                // Content
                Group {
                    switch selectedTab {
                    case .dashboard:
                        DashboardView()
                    case .devices:
                        DevicesView()
                    case .analytics:
                        AnalyticsView()
                    case .ai:
                        AIAssistantView()
                    case .settings:
                        SettingsView()
                    }
                }
                .frame(maxWidth: .infinity, maxHeight: .infinity)
            }
        }
        .background(themeManager.currentTheme.primaryColor)
    }
}

// MARK: - Navigation Button
struct NavigationButton: View {
    let tab: ContentView.Tab
    let isSelected: Bool
    let action: () -> Void
    @EnvironmentObject var themeManager: ThemeManager
    
    var body: some View {
        Button(action: action) {
            HStack(spacing: 12) {
                Image(systemName: tab.icon)
                    .font(.system(size: 16, weight: .medium))
                    .frame(width: 20)
                
                Text(tab.title)
                    .font(.system(size: 14, weight: .medium))
                
                Spacer()
            }
            .padding(.horizontal, 16)
            .padding(.vertical, 12)
            .background(
                RoundedRectangle(cornerRadius: 8)
                    .fill(isSelected ? themeManager.currentTheme.accentColor.opacity(0.15) : Color.clear)
            )
            .foregroundColor(
                isSelected ? themeManager.currentTheme.accentColor : themeManager.currentTheme.textSecondary
            )
        }
        .buttonStyle(PlainButtonStyle())
        .padding(.horizontal, 12)
    }
}

// MARK: - Custom Title Bar
struct CustomTitleBar: View {
    @EnvironmentObject var themeManager: ThemeManager
    
    var body: some View {
        HStack {
            Text("iOS Device Diagnostics")
                .font(.headline)
                .foregroundColor(themeManager.currentTheme.textPrimary)
            
            Spacer()
            
            // Window Controls (placeholder)
            HStack(spacing: 8) {
                Circle()
                    .fill(Color.red)
                    .frame(width: 12, height: 12)
                Circle()
                    .fill(Color.yellow)
                    .frame(width: 12, height: 12)
                Circle()
                    .fill(Color.green)
                    .frame(width: 12, height: 12)
            }
        }
        .padding(.horizontal, 24)
        .padding(.vertical, 16)
        .background(
            themeManager.currentTheme.primaryColor
                .overlay(
                    Rectangle()
                        .fill(themeManager.currentTheme.textSecondary.opacity(0.1))
                        .frame(height: 1),
                    alignment: .bottom
                )
        )
    }
}

// MARK: - Connection Status
struct ConnectionStatusView: View {
    @EnvironmentObject var deviceManager: DeviceManager
    @EnvironmentObject var themeManager: ThemeManager
    
    var body: some View {
        VStack(spacing: 8) {
            HStack {
                Circle()
                    .fill(deviceManager.isConnected ? Color.green : Color.red)
                    .frame(width: 8, height: 8)
                
                Text(deviceManager.isConnected ? "Connected" : "Disconnected")
                    .font(.caption)
                    .foregroundColor(themeManager.currentTheme.textSecondary)
                
                Spacer()
            }
            
            if let device = deviceManager.selectedDevice {
                Text(device.name)
                    .font(.caption2)
                    .foregroundColor(themeManager.currentTheme.textSecondary)
                    .lineLimit(1)
            }
        }
        .padding(.horizontal, 16)
    }
}

// MARK: - Splash View
struct SplashView: View {
    @EnvironmentObject var themeManager: ThemeManager
    @State private var scale: CGFloat = 0.8
    @State private var opacity: Double = 0
    
    var body: some View {
        VStack(spacing: 24) {
            Image(systemName: "eye.circle.fill")
                .font(.system(size: 80, weight: .bold))
                .foregroundColor(themeManager.currentTheme.accentColor)
                .scaleEffect(scale)
                .opacity(opacity)
            
            Text("iSpy")
                .font(.largeTitle)
                .fontWeight(.bold)
                .foregroundColor(themeManager.currentTheme.textPrimary)
                .opacity(opacity)
            
            Text("Advanced iOS Diagnostics")
                .font(.headline)
                .foregroundColor(themeManager.currentTheme.textSecondary)
                .opacity(opacity)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(themeManager.currentTheme.primaryColor)
        .onAppear {
            withAnimation(.easeInOut(duration: 1.2)) {
                scale = 1.0
                opacity = 1.0
            }
        }
    }
}