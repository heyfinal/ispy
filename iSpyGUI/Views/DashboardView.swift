import SwiftUI

struct DashboardView: View {
    @EnvironmentObject var deviceManager: DeviceManager
    @EnvironmentObject var diagnosticsManager: DiagnosticsManager
    @EnvironmentObject var themeManager: ThemeManager
    
    @State private var selectedMetric: DiagnosticModule?
    @State private var showingDetailView = false
    
    let columns = [
        GridItem(.flexible()),
        GridItem(.flexible()),
        GridItem(.flexible())
    ]
    
    var body: some View {
        ScrollView {
            VStack(spacing: 24) {
                // Header Section
                headerSection
                
                // Quick Overview Cards
                if let device = deviceManager.selectedDevice {
                    quickOverviewSection(device: device)
                }
                
                // Diagnostic Modules Grid
                diagnosticModulesSection
                
                // Recent Activity
                recentActivitySection
            }
            .padding(.horizontal, 24)
            .padding(.bottom, 24)
        }
        .background(themeManager.currentTheme.primaryColor)
        .sheet(isPresented: $showingDetailView) {
            if let metric = selectedMetric {
                DiagnosticDetailView(module: metric)
            }
        }
    }
    
    // MARK: - Header Section
    private var headerSection: some View {
        VStack(alignment: .leading, spacing: 16) {
            HStack {
                VStack(alignment: .leading, spacing: 4) {
                    Text("Dashboard")
                        .font(.title)
                        .fontWeight(.bold)
                        .foregroundColor(themeManager.currentTheme.textPrimary)
                    
                    if let device = deviceManager.selectedDevice {
                        Text("Monitoring \(device.name)")
                            .font(.subheadline)
                            .foregroundColor(themeManager.currentTheme.textSecondary)
                    } else {
                        Text("No device selected")
                            .font(.subheadline)
                            .foregroundColor(themeManager.currentTheme.textSecondary)
                    }
                }
                
                Spacer()
                
                // Scan Button
                Button(action: {
                    withAnimation(.spring()) {
                        diagnosticsManager.runFullDiagnostic()
                    }
                }) {
                    HStack(spacing: 8) {
                        Image(systemName: diagnosticsManager.isRunning ? "stop.circle" : "play.circle.fill")
                            .font(.system(size: 16, weight: .medium))
                        
                        Text(diagnosticsManager.isRunning ? "Stop Scan" : "Run Full Scan")
                            .font(.system(size: 14, weight: .semibold))
                    }
                    .foregroundColor(.white)
                    .padding(.horizontal, 16)
                    .padding(.vertical, 10)
                    .background(
                        RoundedRectangle(cornerRadius: 10)
                            .fill(diagnosticsManager.isRunning ? Color.red : themeManager.currentTheme.accentColor)
                    )
                }
                .buttonStyle(PlainButtonStyle())
                .disabled(deviceManager.selectedDevice == nil)
            }
        }
        .padding(.top, 24)
    }
    
    // MARK: - Quick Overview Section
    private func quickOverviewSection(device: Device) -> some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("Quick Overview")
                .font(.headline)
                .fontWeight(.semibold)
                .foregroundColor(themeManager.currentTheme.textPrimary)
            
            HStack(spacing: 16) {
                // Device Health Score
                OverviewCard(
                    title: "Health Score",
                    value: "\(Int(diagnosticsManager.overallHealthScore))",
                    subtitle: "out of 100",
                    color: healthScoreColor,
                    icon: "heart.fill"
                )
                
                // Battery Status
                OverviewCard(
                    title: "Battery",
                    value: "\(device.batteryLevel)%",
                    subtitle: device.batteryStatus.name,
                    color: device.batteryStatus.color,
                    icon: "battery.100"
                )
                
                // Storage Status
                OverviewCard(
                    title: "Storage",
                    value: "\(String(format: "%.1f", device.storagePercentage))%",
                    subtitle: "used",
                    color: storageColor(for: device.storagePercentage),
                    icon: "internaldrive"
                )
                
                // Issues Found
                OverviewCard(
                    title: "Issues",
                    value: "\(diagnosticsManager.criticalIssuesCount)",
                    subtitle: "critical",
                    color: diagnosticsManager.criticalIssuesCount > 0 ? .red : .green,
                    icon: "exclamationmark.triangle.fill"
                )
            }
        }
    }
    
    // MARK: - Diagnostic Modules Section
    private var diagnosticModulesSection: some View {
        VStack(alignment: .leading, spacing: 16) {
            HStack {
                Text("Diagnostic Modules")
                    .font(.headline)
                    .fontWeight(.semibold)
                    .foregroundColor(themeManager.currentTheme.textPrimary)
                
                Spacer()
                
                Text("Last updated: \(diagnosticsManager.lastUpdateTime)")
                    .font(.caption)
                    .foregroundColor(themeManager.currentTheme.textSecondary)
            }
            
            LazyVGrid(columns: columns, spacing: 16) {
                ForEach(diagnosticsManager.modules) { module in
                    DiagnosticModuleCard(module: module) {
                        selectedMetric = module
                        showingDetailView = true
                    }
                }
            }
        }
    }
    
    // MARK: - Recent Activity Section
    private var recentActivitySection: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("Recent Activity")
                .font(.headline)
                .fontWeight(.semibold)
                .foregroundColor(themeManager.currentTheme.textPrimary)
            
            VStack(spacing: 12) {
                ForEach(diagnosticsManager.recentActivities.prefix(5), id: \.id) { activity in
                    ActivityRow(activity: activity)
                }
            }
            .padding(16)
            .background(
                RoundedRectangle(cornerRadius: 12)
                    .fill(themeManager.currentTheme.secondaryColor)
            )
        }
    }
    
    // MARK: - Computed Properties
    private var healthScoreColor: Color {
        let score = diagnosticsManager.overallHealthScore
        if score >= 80 {
            return .green
        } else if score >= 60 {
            return .orange
        } else {
            return .red
        }
    }
    
    private func storageColor(for percentage: Double) -> Color {
        if percentage > 85 {
            return .red
        } else if percentage > 70 {
            return .orange
        } else {
            return .blue
        }
    }
}

// MARK: - Overview Card
struct OverviewCard: View {
    let title: String
    let value: String
    let subtitle: String
    let color: Color
    let icon: String
    @EnvironmentObject var themeManager: ThemeManager
    
    var body: some View {
        VStack(spacing: 12) {
            HStack {
                Image(systemName: icon)
                    .font(.system(size: 20, weight: .medium))
                    .foregroundColor(color)
                
                Spacer()
                
                Text(value)
                    .font(.title2)
                    .fontWeight(.bold)
                    .foregroundColor(themeManager.currentTheme.textPrimary)
            }
            
            VStack(alignment: .leading, spacing: 4) {
                Text(title)
                    .font(.subheadline)
                    .fontWeight(.medium)
                    .foregroundColor(themeManager.currentTheme.textPrimary)
                
                Text(subtitle)
                    .font(.caption)
                    .foregroundColor(themeManager.currentTheme.textSecondary)
            }
        }
        .padding(16)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(
            RoundedRectangle(cornerRadius: 12)
                .fill(themeManager.currentTheme.secondaryColor)
                .overlay(
                    RoundedRectangle(cornerRadius: 12)
                        .stroke(color.opacity(0.3), lineWidth: 1)
                )
        )
    }
}

// MARK: - Diagnostic Module Card
struct DiagnosticModuleCard: View {
    let module: DiagnosticModule
    let onTap: () -> Void
    @EnvironmentObject var themeManager: ThemeManager
    
    var body: some View {
        Button(action: onTap) {
            VStack(spacing: 12) {
                // Status Indicator
                HStack {
                    Image(systemName: module.status.icon)
                        .font(.system(size: 16, weight: .medium))
                        .foregroundColor(module.status.color)
                    
                    Spacer()
                    
                    if module.isRunning {
                        ProgressView()
                            .scaleEffect(0.8)
                            .progressViewStyle(CircularProgressViewStyle(tint: themeManager.currentTheme.accentColor))
                    }
                }
                
                // Module Info
                VStack(alignment: .leading, spacing: 4) {
                    Text(module.name)
                        .font(.subheadline)
                        .fontWeight(.semibold)
                        .foregroundColor(themeManager.currentTheme.textPrimary)
                        .lineLimit(1)
                    
                    Text(module.description)
                        .font(.caption)
                        .foregroundColor(themeManager.currentTheme.textSecondary)
                        .lineLimit(2)
                }
                .frame(maxWidth: .infinity, alignment: .leading)
                
                // Score Bar
                VStack(spacing: 4) {
                    HStack {
                        Text("Score")
                            .font(.caption2)
                            .foregroundColor(themeManager.currentTheme.textSecondary)
                        
                        Spacer()
                        
                        Text("\(Int(module.score))/100")
                            .font(.caption2)
                            .fontWeight(.medium)
                            .foregroundColor(themeManager.currentTheme.textPrimary)
                    }
                    
                    ProgressView(value: module.score, total: 100)
                        .progressViewStyle(CustomProgressViewStyle(color: module.status.color))
                }
            }
            .padding(16)
            .background(
                RoundedRectangle(cornerRadius: 12)
                    .fill(themeManager.currentTheme.secondaryColor)
                    .overlay(
                        RoundedRectangle(cornerRadius: 12)
                            .stroke(module.status.color.opacity(0.3), lineWidth: 1)
                    )
            )
        }
        .buttonStyle(PlainButtonStyle())
    }
}

// MARK: - Activity Row
struct ActivityRow: View {
    let activity: ActivityItem
    @EnvironmentObject var themeManager: ThemeManager
    
    var body: some View {
        HStack(spacing: 12) {
            Circle()
                .fill(activity.type.color)
                .frame(width: 8, height: 8)
            
            VStack(alignment: .leading, spacing: 2) {
                Text(activity.title)
                    .font(.subheadline)
                    .foregroundColor(themeManager.currentTheme.textPrimary)
                
                Text(activity.subtitle)
                    .font(.caption)
                    .foregroundColor(themeManager.currentTheme.textSecondary)
            }
            
            Spacer()
            
            Text(activity.timeAgo)
                .font(.caption)
                .foregroundColor(themeManager.currentTheme.textSecondary)
        }
    }
}

// MARK: - Extensions
extension Device.BatteryStatus {
    var name: String {
        switch self {
        case .critical: return "Critical"
        case .low: return "Low"
        case .good: return "Good"
        case .excellent: return "Excellent"
        }
    }
}