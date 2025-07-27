import SwiftUI

struct SettingsView: View {
    @EnvironmentObject var themeManager: ThemeManager
    @State private var showingAbout = false
    @State private var autoScanEnabled = true
    @State private var notificationsEnabled = true
    @State private var analyticsEnabled = true
    @State private var scanInterval: Double = 30
    @State private var apiKey = ""
    @State private var showingAPIKeyAlert = false
    
    var body: some View {
        ScrollView {
            VStack(spacing: 24) {
                // Header
                headerSection
                
                // AI Settings
                aiSettingsSection
                
                // Scanning Settings
                scanningSettingsSection
                
                // Notifications
                notificationsSection
                
                // Data & Privacy
                dataPrivacySection
                
                // About & Support
                aboutSection
            }
            .padding(.horizontal, 24)
            .padding(.bottom, 24)
        }
        .background(themeManager.currentTheme.primaryColor)
        .sheet(isPresented: $showingAbout) {
            AboutView()
        }
        .alert("API Key Required", isPresented: $showingAPIKeyAlert) {
            TextField("Enter API Key", text: $apiKey)
            Button("Save") {
                // Save API key logic
            }
            Button("Cancel", role: .cancel) {}
        } message: {
            Text("Enter your OpenAI API key to enable AI-powered diagnostics and recommendations.")
        }
    }
    
    // MARK: - Header Section
    private var headerSection: some View {
        HStack {
            VStack(alignment: .leading, spacing: 4) {
                Text("Settings")
                    .font(.title2)
                    .fontWeight(.bold)
                    .foregroundColor(themeManager.currentTheme.textPrimary)
                
                Text("Customize your iSpy experience")
                    .font(.subheadline)
                    .foregroundColor(themeManager.currentTheme.textSecondary)
            }
            
            Spacer()
            
            // Settings Icon
            Image(systemName: "gear")
                .font(.system(size: 24, weight: .medium))
                .foregroundColor(themeManager.currentTheme.accentColor)
        }
        .padding(.top, 24)
    }
    
    // MARK: - AI Settings Section
    private var aiSettingsSection: some View {
        SettingsSection(title: "AI Assistant", icon: "brain.head.profile") {
            VStack(spacing: 16) {
                SettingsRow(
                    title: "API Configuration",
                    subtitle: apiKey.isEmpty ? "API key not configured" : "API key configured",
                    icon: "key",
                    showChevron: true
                ) {
                    showingAPIKeyAlert = true
                }
                
                SettingsToggleRow(
                    title: "Smart Recommendations",
                    subtitle: "Get AI-powered optimization suggestions",
                    icon: "lightbulb",
                    isOn: $analyticsEnabled
                )
                
                SettingsRow(
                    title: "AI Model",
                    subtitle: "GPT-4 (Recommended)",
                    icon: "cpu",
                    showChevron: true
                ) {
                    // Model selection logic
                }
            }
        }
    }
    
    // MARK: - Scanning Settings Section
    private var scanningSettingsSection: some View {
        SettingsSection(title: "Diagnostics", icon: "magnifyingglass") {
            VStack(spacing: 16) {
                SettingsToggleRow(
                    title: "Auto Scan",
                    subtitle: "Automatically run diagnostics when device connects",
                    icon: "autostartstop",
                    isOn: $autoScanEnabled
                )
                
                VStack(alignment: .leading, spacing: 8) {
                    HStack {
                        Image(systemName: "timer")
                            .font(.system(size: 16, weight: .medium))
                            .foregroundColor(themeManager.currentTheme.accentColor)
                            .frame(width: 24)
                        
                        VStack(alignment: .leading, spacing: 2) {
                            Text("Scan Interval")
                                .font(.subheadline)
                                .fontWeight(.medium)
                                .foregroundColor(themeManager.currentTheme.textPrimary)
                            
                            Text("\(Int(scanInterval)) minutes")
                                .font(.caption)
                                .foregroundColor(themeManager.currentTheme.textSecondary)
                        }
                        
                        Spacer()
                    }
                    
                    Slider(value: $scanInterval, in: 5...120, step: 5) {
                        Text("Interval")
                    }
                    .tint(themeManager.currentTheme.accentColor)
                }
                .padding(16)
                .background(
                    RoundedRectangle(cornerRadius: 12)
                        .fill(themeManager.currentTheme.primaryColor)
                )
                
                SettingsRow(
                    title: "Module Selection",
                    subtitle: "Choose which diagnostics to run",
                    icon: "checkmark.circle",
                    showChevron: true
                ) {
                    // Module selection logic
                }
            }
        }
    }
    
    // MARK: - Notifications Section
    private var notificationsSection: some View {
        SettingsSection(title: "Notifications", icon: "bell") {
            VStack(spacing: 16) {
                SettingsToggleRow(
                    title: "Enable Notifications",
                    subtitle: "Get alerts for critical issues",
                    icon: "bell.badge",
                    isOn: $notificationsEnabled
                )
                
                if notificationsEnabled {
                    VStack(spacing: 12) {
                        NotificationTypeRow(
                            title: "Critical Issues",
                            isEnabled: true
                        )
                        
                        NotificationTypeRow(
                            title: "Recommendations",
                            isEnabled: true
                        )
                        
                        NotificationTypeRow(
                            title: "Scan Complete",
                            isEnabled: false
                        )
                    }
                    .padding(16)
                    .background(
                        RoundedRectangle(cornerRadius: 12)
                            .fill(themeManager.currentTheme.primaryColor)
                    )
                }
            }
        }
    }
    
    // MARK: - Data & Privacy Section
    private var dataPrivacySection: some View {
        SettingsSection(title: "Data & Privacy", icon: "lock.shield") {
            VStack(spacing: 16) {
                SettingsRow(
                    title: "Data Collection",
                    subtitle: "All data processed locally",
                    icon: "server.rack",
                    showChevron: false
                ) {}
                
                SettingsRow(
                    title: "Export Data",
                    subtitle: "Export your diagnostic history",
                    icon: "square.and.arrow.up",
                    showChevron: true
                ) {
                    // Export data logic
                }
                
                SettingsRow(
                    title: "Clear History",
                    subtitle: "Remove all stored diagnostic data",
                    icon: "trash",
                    showChevron: true,
                    isDestructive: true
                ) {
                    // Clear history logic
                }
            }
        }
    }
    
    // MARK: - About Section
    private var aboutSection: some View {
        SettingsSection(title: "About & Support", icon: "info.circle") {
            VStack(spacing: 16) {
                SettingsRow(
                    title: "About iSpy",
                    subtitle: "Version 1.0.0",
                    icon: "info",
                    showChevron: true
                ) {
                    showingAbout = true
                }
                
                SettingsRow(
                    title: "Check for Updates",
                    subtitle: "You're up to date",
                    icon: "arrow.clockwise",
                    showChevron: true
                ) {
                    // Check updates logic
                }
                
                SettingsRow(
                    title: "Documentation",
                    subtitle: "User guide and troubleshooting",
                    icon: "book",
                    showChevron: true
                ) {
                    // Open documentation
                }
                
                SettingsRow(
                    title: "Send Feedback",
                    subtitle: "Help us improve iSpy",
                    icon: "envelope",
                    showChevron: true
                ) {
                    // Send feedback logic
                }
            }
        }
    }
}

// MARK: - Settings Section
struct SettingsSection<Content: View>: View {
    let title: String
    let icon: String
    let content: Content
    @EnvironmentObject var themeManager: ThemeManager
    
    init(title: String, icon: String, @ViewBuilder content: () -> Content) {
        self.title = title
        self.icon = icon
        self.content = content()
    }
    
    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            HStack(spacing: 8) {
                Image(systemName: icon)
                    .font(.system(size: 16, weight: .medium))
                    .foregroundColor(themeManager.currentTheme.accentColor)
                
                Text(title)
                    .font(.headline)
                    .fontWeight(.semibold)
                    .foregroundColor(themeManager.currentTheme.textPrimary)
            }
            
            VStack(spacing: 12) {
                content
            }
            .padding(20)
            .background(
                RoundedRectangle(cornerRadius: 16)
                    .fill(themeManager.currentTheme.secondaryColor)
            )
        }
    }
}

// MARK: - Settings Row
struct SettingsRow: View {
    let title: String
    let subtitle: String
    let icon: String
    let showChevron: Bool
    let isDestructive: Bool
    let action: () -> Void
    @EnvironmentObject var themeManager: ThemeManager
    
    init(
        title: String,
        subtitle: String,
        icon: String,
        showChevron: Bool = true,
        isDestructive: Bool = false,
        action: @escaping () -> Void
    ) {
        self.title = title
        self.subtitle = subtitle
        self.icon = icon
        self.showChevron = showChevron
        self.isDestructive = isDestructive
        self.action = action
    }
    
    var body: some View {
        Button(action: action) {
            HStack(spacing: 12) {
                Image(systemName: icon)
                    .font(.system(size: 16, weight: .medium))
                    .foregroundColor(isDestructive ? .red : themeManager.currentTheme.accentColor)
                    .frame(width: 24)
                
                VStack(alignment: .leading, spacing: 2) {
                    Text(title)
                        .font(.subheadline)
                        .fontWeight(.medium)
                        .foregroundColor(isDestructive ? .red : themeManager.currentTheme.textPrimary)
                    
                    Text(subtitle)
                        .font(.caption)
                        .foregroundColor(themeManager.currentTheme.textSecondary)
                }
                
                Spacer()
                
                if showChevron {
                    Image(systemName: "chevron.right")
                        .font(.caption)
                        .foregroundColor(themeManager.currentTheme.textSecondary)
                }
            }
            .padding(16)
            .background(
                RoundedRectangle(cornerRadius: 12)
                    .fill(themeManager.currentTheme.primaryColor)
            )
        }
        .buttonStyle(PlainButtonStyle())
    }
}

// MARK: - Settings Toggle Row
struct SettingsToggleRow: View {
    let title: String
    let subtitle: String
    let icon: String
    @Binding var isOn: Bool
    @EnvironmentObject var themeManager: ThemeManager
    
    var body: some View {
        HStack(spacing: 12) {
            Image(systemName: icon)
                .font(.system(size: 16, weight: .medium))
                .foregroundColor(themeManager.currentTheme.accentColor)
                .frame(width: 24)
            
            VStack(alignment: .leading, spacing: 2) {
                Text(title)
                    .font(.subheadline)
                    .fontWeight(.medium)
                    .foregroundColor(themeManager.currentTheme.textPrimary)
                
                Text(subtitle)
                    .font(.caption)
                    .foregroundColor(themeManager.currentTheme.textSecondary)
            }
            
            Spacer()
            
            Toggle("", isOn: $isOn)
                .toggleStyle(SwitchToggleStyle(tint: themeManager.currentTheme.accentColor))
        }
        .padding(16)
        .background(
            RoundedRectangle(cornerRadius: 12)
                .fill(themeManager.currentTheme.primaryColor)
        )
    }
}

// MARK: - Notification Type Row
struct NotificationTypeRow: View {
    let title: String
    @State var isEnabled: Bool
    @EnvironmentObject var themeManager: ThemeManager
    
    var body: some View {
        HStack {
            Text(title)
                .font(.caption)
                .foregroundColor(themeManager.currentTheme.textPrimary)
            
            Spacer()
            
            Toggle("", isOn: $isEnabled)
                .toggleStyle(SwitchToggleStyle(tint: themeManager.currentTheme.accentColor))
                .scaleEffect(0.8)
        }
    }
}

// MARK: - About View
struct AboutView: View {
    @EnvironmentObject var themeManager: ThemeManager
    @Environment(\.dismiss) private var dismiss
    
    var body: some View {
        NavigationView {
            ScrollView {
                VStack(spacing: 32) {
                    // App Icon and Info
                    VStack(spacing: 16) {
                        Image(systemName: "eye.circle.fill")
                            .font(.system(size: 80, weight: .bold))
                            .foregroundColor(themeManager.currentTheme.accentColor)
                        
                        VStack(spacing: 8) {
                            Text("iSpy")
                                .font(.largeTitle)
                                .fontWeight(.bold)
                                .foregroundColor(themeManager.currentTheme.textPrimary)
                            
                            Text("Advanced iOS Diagnostics")
                                .font(.headline)
                                .foregroundColor(themeManager.currentTheme.textSecondary)
                            
                            Text("Version 1.0.0 (Build 1)")
                                .font(.caption)
                                .foregroundColor(themeManager.currentTheme.textSecondary)
                        }
                    }
                    
                    // Description
                    VStack(alignment: .leading, spacing: 16) {
                        Text("About iSpy")
                            .font(.headline)
                            .fontWeight(.semibold)
                            .foregroundColor(themeManager.currentTheme.textPrimary)
                        
                        Text("iSpy is the most comprehensive iOS device diagnostic and management tool available. With AI-powered analysis, advanced analytics, and comprehensive device insights, iSpy helps you keep your iOS devices running at peak performance.")
                            .font(.body)
                            .foregroundColor(themeManager.currentTheme.textSecondary)
                            .fixedSize(horizontal: false, vertical: true)
                    }
                    
                    // Features
                    VStack(alignment: .leading, spacing: 16) {
                        Text("Features")
                            .font(.headline)
                            .fontWeight(.semibold)
                            .foregroundColor(themeManager.currentTheme.textPrimary)
                        
                        VStack(alignment: .leading, spacing: 8) {
                            FeatureRow(icon: "battery.100", text: "Battery Health Analysis")
                            FeatureRow(icon: "internaldrive", text: "Storage Optimization")
                            FeatureRow(icon: "brain.head.profile", text: "AI-Powered Diagnostics")
                            FeatureRow(icon: "chart.line.uptrend.xyaxis", text: "Advanced Analytics")
                            FeatureRow(icon: "shield.checkered", text: "Security Assessment")
                            FeatureRow(icon: "speedometer", text: "Performance Monitoring")
                        }
                    }
                    
                    // Credits
                    VStack(alignment: .leading, spacing: 16) {
                        Text("Credits")
                            .font(.headline)
                            .fontWeight(.semibold)
                            .foregroundColor(themeManager.currentTheme.textPrimary)
                        
                        Text("Built with SwiftUI and powered by advanced iOS diagnostic technologies. Special thanks to the open-source community and the libimobiledevice project.")
                            .font(.body)
                            .foregroundColor(themeManager.currentTheme.textSecondary)
                            .fixedSize(horizontal: false, vertical: true)
                    }
                    
                    // Copyright
                    Text("© 2024 iSpy Development Team. All rights reserved.")
                        .font(.caption)
                        .foregroundColor(themeManager.currentTheme.textSecondary)
                        .multilineTextAlignment(.center)
                }
                .padding(24)
            }
            .background(themeManager.currentTheme.primaryColor)
            .navigationTitle("About")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Done") {
                        dismiss()
                    }
                    .foregroundColor(themeManager.currentTheme.accentColor)
                }
            }
        }
    }
}

// MARK: - Feature Row
struct FeatureRow: View {
    let icon: String
    let text: String
    @EnvironmentObject var themeManager: ThemeManager
    
    var body: some View {
        HStack(spacing: 12) {
            Image(systemName: icon)
                .font(.system(size: 14, weight: .medium))
                .foregroundColor(themeManager.currentTheme.accentColor)
                .frame(width: 20)
            
            Text(text)
                .font(.subheadline)
                .foregroundColor(themeManager.currentTheme.textPrimary)
            
            Spacer()
        }
    }
}