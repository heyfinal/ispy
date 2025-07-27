import SwiftUI

struct DeviceDetailView: View {
    let device: Device
    @EnvironmentObject var themeManager: ThemeManager
    @Environment(\.dismiss) private var dismiss
    @State private var selectedTab: DetailTab = .overview
    
    enum DetailTab: String, CaseIterable {
        case overview = "Overview"
        case diagnostics = "Diagnostics"
        case analytics = "Analytics"
        case logs = "Logs"
        
        var icon: String {
            switch self {
            case .overview: return "info.circle"
            case .diagnostics: return "stethoscope"
            case .analytics: return "chart.bar"
            case .logs: return "doc.text"
            }
        }
    }
    
    var body: some View {
        NavigationView {
            VStack(spacing: 0) {
                // Header
                deviceHeader
                
                // Tab Selector
                tabSelector
                
                // Content
                ScrollView {
                    VStack(spacing: 20) {
                        switch selectedTab {
                        case .overview:
                            overviewContent
                        case .diagnostics:
                            diagnosticsContent
                        case .analytics:
                            analyticsContent
                        case .logs:
                            logsContent
                        }
                    }
                    .padding(.horizontal, 24)
                    .padding(.bottom, 24)
                }
            }
            .background(themeManager.currentTheme.primaryColor)
            .navigationTitle("Device Details")
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
    
    // MARK: - Device Header
    private var deviceHeader: some View {
        VStack(spacing: 16) {
            // Device Icon
            Image(systemName: device.model.contains("iPad") ? "ipad" : "iphone")
                .font(.system(size: 48, weight: .medium))
                .foregroundColor(themeManager.currentTheme.accentColor)
            
            // Device Info
            VStack(spacing: 8) {
                Text(device.name)
                    .font(.title2)
                    .fontWeight(.bold)
                    .foregroundColor(themeManager.currentTheme.textPrimary)
                
                Text(device.model)
                    .font(.headline)
                    .foregroundColor(themeManager.currentTheme.textSecondary)
                
                HStack(spacing: 16) {
                    Label("iOS \(device.version)", systemImage: "apple.logo")
                    Label(device.isConnected ? "Connected" : "Disconnected", 
                          systemImage: device.isConnected ? "checkmark.circle.fill" : "xmark.circle.fill")
                        .foregroundColor(device.isConnected ? .green : .red)
                }
                .font(.caption)
                .foregroundColor(themeManager.currentTheme.textSecondary)
            }
        }
        .padding(.vertical, 24)
    }
    
    // MARK: - Tab Selector
    private var tabSelector: some View {
        HStack(spacing: 0) {
            ForEach(DetailTab.allCases, id: \.self) { tab in
                Button(action: {
                    withAnimation(.easeInOut(duration: 0.2)) {
                        selectedTab = tab
                    }
                }) {
                    VStack(spacing: 4) {
                        Image(systemName: tab.icon)
                            .font(.system(size: 16, weight: .medium))
                        Text(tab.rawValue)
                            .font(.caption)
                            .fontWeight(.medium)
                    }
                    .foregroundColor(selectedTab == tab ? themeManager.currentTheme.accentColor : themeManager.currentTheme.textSecondary)
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 12)
                    .background(
                        Rectangle()
                            .fill(selectedTab == tab ? themeManager.currentTheme.accentColor.opacity(0.1) : Color.clear)
                    )
                }
                .buttonStyle(PlainButtonStyle())
            }
        }
        .background(themeManager.currentTheme.secondaryColor)
        .overlay(alignment: .bottom) {
            Rectangle()
                .fill(themeManager.currentTheme.textSecondary.opacity(0.2))
                .frame(height: 1)
        }
    }
    
    // MARK: - Overview Content
    private var overviewContent: some View {
        VStack(spacing: 20) {
            // Quick Stats
            HStack(spacing: 16) {
                StatCard(
                    title: "Battery",
                    value: "\(device.batteryLevel)%",
                    icon: "battery.100",
                    color: device.batteryStatus.color
                )
                
                StatCard(
                    title: "Storage",
                    value: "\(String(format: "%.1f", device.storagePercentage))%",
                    icon: "internaldrive",
                    color: storageColor
                )
            }
            
            // Device Specifications
            SpecificationSection(device: device)
            
            // Recent Activity
            RecentActivitySection()
        }
    }
    
    // MARK: - Diagnostics Content
    private var diagnosticsContent: some View {
        VStack(spacing: 20) {
            DiagnosticModulesList()
        }
    }
    
    // MARK: - Analytics Content
    private var analyticsContent: some View {
        VStack(spacing: 20) {
            Text("Analytics data would be displayed here")
                .foregroundColor(themeManager.currentTheme.textSecondary)
                .frame(maxWidth: .infinity, minHeight: 200)
        }
    }
    
    // MARK: - Logs Content
    private var logsContent: some View {
        VStack(spacing: 20) {
            LogsSection()
        }
    }
    
    // MARK: - Computed Properties
    private var storageColor: Color {
        let percentage = device.storagePercentage
        if percentage > 85 {
            return .red
        } else if percentage > 70 {
            return .orange
        } else {
            return .blue
        }
    }
}

// MARK: - Stat Card
struct StatCard: View {
    let title: String
    let value: String
    let icon: String
    let color: Color
    @EnvironmentObject var themeManager: ThemeManager
    
    var body: some View {
        VStack(spacing: 12) {
            Image(systemName: icon)
                .font(.system(size: 24, weight: .medium))
                .foregroundColor(color)
            
            VStack(spacing: 4) {
                Text(value)
                    .font(.title2)
                    .fontWeight(.bold)
                    .foregroundColor(themeManager.currentTheme.textPrimary)
                
                Text(title)
                    .font(.caption)
                    .foregroundColor(themeManager.currentTheme.textSecondary)
            }
        }
        .frame(maxWidth: .infinity)
        .padding(20)
        .background(
            RoundedRectangle(cornerRadius: 16)
                .fill(themeManager.currentTheme.secondaryColor)
                .overlay(
                    RoundedRectangle(cornerRadius: 16)
                        .stroke(color.opacity(0.3), lineWidth: 1)
                )
        )
    }
}

// MARK: - Specification Section
struct SpecificationSection: View {
    let device: Device
    @EnvironmentObject var themeManager: ThemeManager
    
    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("Specifications")
                .font(.headline)
                .fontWeight(.semibold)
                .foregroundColor(themeManager.currentTheme.textPrimary)
            
            VStack(spacing: 12) {
                SpecRow(title: "Model", value: device.model)
                SpecRow(title: "iOS Version", value: device.version)
                SpecRow(title: "UDID", value: String(device.udid.prefix(8)) + "...")
                SpecRow(title: "Total Storage", value: "\(String(format: "%.0f", device.storageTotal)) GB")
                SpecRow(title: "Available Storage", value: "\(String(format: "%.1f", device.storageTotal - device.storageUsed)) GB")
                SpecRow(title: "Connection", value: device.isConnected ? "USB Connected" : "Disconnected")
            }
            .padding(16)
            .background(
                RoundedRectangle(cornerRadius: 12)
                    .fill(themeManager.currentTheme.secondaryColor)
            )
        }
    }
}

// MARK: - Spec Row
struct SpecRow: View {
    let title: String
    let value: String
    @EnvironmentObject var themeManager: ThemeManager
    
    var body: some View {
        HStack {
            Text(title)
                .font(.subheadline)
                .foregroundColor(themeManager.currentTheme.textSecondary)
            
            Spacer()
            
            Text(value)
                .font(.subheadline)
                .fontWeight(.medium)
                .foregroundColor(themeManager.currentTheme.textPrimary)
        }
    }
}

// MARK: - Recent Activity Section
struct RecentActivitySection: View {
    @EnvironmentObject var themeManager: ThemeManager
    
    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("Recent Activity")
                .font(.headline)
                .fontWeight(.semibold)
                .foregroundColor(themeManager.currentTheme.textPrimary)
            
            VStack(spacing: 12) {
                ActivityItemRow(
                    icon: "checkmark.circle.fill",
                    iconColor: .green,
                    title: "Battery diagnostic completed",
                    subtitle: "2 minutes ago"
                )
                
                ActivityItemRow(
                    icon: "info.circle.fill",
                    iconColor: .blue,
                    title: "Storage analysis finished",
                    subtitle: "5 minutes ago"
                )
                
                ActivityItemRow(
                    icon: "exclamationmark.triangle.fill",
                    iconColor: .orange,
                    title: "Backup issue detected",
                    subtitle: "12 minutes ago"
                )
            }
            .padding(16)
            .background(
                RoundedRectangle(cornerRadius: 12)
                    .fill(themeManager.currentTheme.secondaryColor)
            )
        }
    }
}

// MARK: - Activity Item Row
struct ActivityItemRow: View {
    let icon: String
    let iconColor: Color
    let title: String
    let subtitle: String
    @EnvironmentObject var themeManager: ThemeManager
    
    var body: some View {
        HStack(spacing: 12) {
            Image(systemName: icon)
                .font(.system(size: 14, weight: .medium))
                .foregroundColor(iconColor)
                .frame(width: 20)
            
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
        }
    }
}

// MARK: - Diagnostic Modules List
struct DiagnosticModulesList: View {
    @EnvironmentObject var themeManager: ThemeManager
    
    let modules = [
        ("Battery Health", "battery.100", 87, Color.green),
        ("Storage Analysis", "internaldrive", 92, Color.blue),
        ("Security Scan", "shield.checkered", 94, Color.green),
        ("Performance", "speedometer", 78, Color.orange),
        ("Network", "wifi", 85, Color.blue),
        ("Thermal", "thermometer", 96, Color.green)
    ]
    
    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("Diagnostic Modules")
                .font(.headline)
                .fontWeight(.semibold)
                .foregroundColor(themeManager.currentTheme.textPrimary)
            
            VStack(spacing: 12) {
                ForEach(modules, id: \.0) { module in
                    DiagnosticModuleRow(
                        name: module.0,
                        icon: module.1,
                        score: module.2,
                        color: module.3
                    )
                }
            }
        }
    }
}

// MARK: - Diagnostic Module Row
struct DiagnosticModuleRow: View {
    let name: String
    let icon: String
    let score: Int
    let color: Color
    @EnvironmentObject var themeManager: ThemeManager
    
    var body: some View {
        HStack(spacing: 12) {
            Image(systemName: icon)
                .font(.system(size: 16, weight: .medium))
                .foregroundColor(color)
                .frame(width: 24)
            
            VStack(alignment: .leading, spacing: 2) {
                Text(name)
                    .font(.subheadline)
                    .fontWeight(.medium)
                    .foregroundColor(themeManager.currentTheme.textPrimary)
                
                Text("Score: \(score)/100")
                    .font(.caption)
                    .foregroundColor(themeManager.currentTheme.textSecondary)
            }
            
            Spacer()
            
            // Progress Circle
            ZStack {
                Circle()
                    .stroke(color.opacity(0.2), lineWidth: 3)
                    .frame(width: 32, height: 32)
                
                Circle()
                    .trim(from: 0, to: CGFloat(score) / 100)
                    .stroke(color, style: StrokeStyle(lineWidth: 3, lineCap: .round))
                    .frame(width: 32, height: 32)
                    .rotationEffect(.degrees(-90))
                
                Text("\(score)")
                    .font(.caption2)
                    .fontWeight(.bold)
                    .foregroundColor(themeManager.currentTheme.textPrimary)
            }
        }
        .padding(16)
        .background(
            RoundedRectangle(cornerRadius: 12)
                .fill(themeManager.currentTheme.secondaryColor)
        )
    }
}

// MARK: - Logs Section
struct LogsSection: View {
    @EnvironmentObject var themeManager: ThemeManager
    
    let logs = [
        LogEntry(timestamp: "14:32:15", level: .info, message: "Battery diagnostic started"),
        LogEntry(timestamp: "14:32:18", level: .success, message: "Battery health check completed - 87%"),
        LogEntry(timestamp: "14:32:20", level: .info, message: "Storage analysis initiated"),
        LogEntry(timestamp: "14:32:25", level: .warning, message: "Low storage warning - 85% used"),
        LogEntry(timestamp: "14:32:30", level: .success, message: "Security scan completed successfully"),
        LogEntry(timestamp: "14:32:35", level: .error, message: "Backup verification failed - no recent backup")
    ]
    
    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            HStack {
                Text("Diagnostic Logs")
                    .font(.headline)
                    .fontWeight(.semibold)
                    .foregroundColor(themeManager.currentTheme.textPrimary)
                
                Spacer()
                
                Button("Clear") {
                    // Clear logs action
                }
                .font(.caption)
                .foregroundColor(themeManager.currentTheme.accentColor)
            }
            
            VStack(spacing: 8) {
                ForEach(logs) { log in
                    LogRow(log: log)
                }
            }
            .padding(16)
            .background(
                RoundedRectangle(cornerRadius: 12)
                    .fill(themeManager.currentTheme.secondaryColor)
            )
        }
    }
}

// MARK: - Log Entry Model
struct LogEntry: Identifiable {
    let id = UUID()
    let timestamp: String
    let level: LogLevel
    let message: String
    
    enum LogLevel {
        case info, success, warning, error
        
        var color: Color {
            switch self {
            case .info: return .blue
            case .success: return .green
            case .warning: return .orange
            case .error: return .red
            }
        }
        
        var icon: String {
            switch self {
            case .info: return "info.circle"
            case .success: return "checkmark.circle"
            case .warning: return "exclamationmark.triangle"
            case .error: return "xmark.circle"
            }
        }
    }
}

// MARK: - Log Row
struct LogRow: View {
    let log: LogEntry
    @EnvironmentObject var themeManager: ThemeManager
    
    var body: some View {
        HStack(spacing: 8) {
            Text(log.timestamp)
                .font(.caption2)
                .fontFamily(.monospaced)
                .foregroundColor(themeManager.currentTheme.textSecondary)
                .frame(width: 60, alignment: .leading)
            
            Image(systemName: log.level.icon)
                .font(.caption)
                .foregroundColor(log.level.color)
                .frame(width: 16)
            
            Text(log.message)
                .font(.caption)
                .foregroundColor(themeManager.currentTheme.textPrimary)
                .fixedSize(horizontal: false, vertical: true)
            
            Spacer()
        }
    }
}

// MARK: - Diagnostic Detail View
struct DiagnosticDetailView: View {
    let module: DiagnosticModule
    @EnvironmentObject var themeManager: ThemeManager
    @Environment(\.dismiss) private var dismiss
    
    var body: some View {
        NavigationView {
            ScrollView {
                VStack(spacing: 24) {
                    // Module Header
                    VStack(spacing: 16) {
                        Image(systemName: module.icon)
                            .font(.system(size: 48, weight: .medium))
                            .foregroundColor(module.status.color)
                        
                        VStack(spacing: 8) {
                            Text(module.name)
                                .font(.title2)
                                .fontWeight(.bold)
                                .foregroundColor(themeManager.currentTheme.textPrimary)
                            
                            Text(module.description)
                                .font(.subheadline)
                                .foregroundColor(themeManager.currentTheme.textSecondary)
                                .multilineTextAlignment(.center)
                        }
                    }
                    
                    // Score Card
                    VStack(spacing: 16) {
                        Text("Current Score")
                            .font(.headline)
                            .foregroundColor(themeManager.currentTheme.textPrimary)
                        
                        ZStack {
                            Circle()
                                .stroke(module.status.color.opacity(0.2), lineWidth: 8)
                                .frame(width: 120, height: 120)
                            
                            Circle()
                                .trim(from: 0, to: CGFloat(module.score) / 100)
                                .stroke(module.status.color, style: StrokeStyle(lineWidth: 8, lineCap: .round))
                                .frame(width: 120, height: 120)
                                .rotationEffect(.degrees(-90))
                            
                            VStack(spacing: 4) {
                                Text("\(Int(module.score))")
                                    .font(.largeTitle)
                                    .fontWeight(.bold)
                                    .foregroundColor(themeManager.currentTheme.textPrimary)
                                
                                Text("out of 100")
                                    .font(.caption)
                                    .foregroundColor(themeManager.currentTheme.textSecondary)
                            }
                        }
                    }
                    
                    // Recommendations
                    VStack(alignment: .leading, spacing: 16) {
                        Text("Recommendations")
                            .font(.headline)
                            .fontWeight(.semibold)
                            .foregroundColor(themeManager.currentTheme.textPrimary)
                        
                        VStack(spacing: 12) {
                            ForEach(module.recommendations, id: \.self) { recommendation in
                                HStack(alignment: .top, spacing: 12) {
                                    Image(systemName: "lightbulb")
                                        .font(.system(size: 14, weight: .medium))
                                        .foregroundColor(themeManager.currentTheme.accentColor)
                                        .frame(width: 20)
                                    
                                    Text(recommendation)
                                        .font(.subheadline)
                                        .foregroundColor(themeManager.currentTheme.textPrimary)
                                        .fixedSize(horizontal: false, vertical: true)
                                    
                                    Spacer()
                                }
                            }
                        }
                        .padding(16)
                        .background(
                            RoundedRectangle(cornerRadius: 12)
                                .fill(themeManager.currentTheme.secondaryColor)
                        )
                    }
                }
                .padding(24)
            }
            .background(themeManager.currentTheme.primaryColor)
            .navigationTitle("Module Details")
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