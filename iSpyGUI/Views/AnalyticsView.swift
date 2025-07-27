import SwiftUI
import Charts

struct AnalyticsView: View {
    @EnvironmentObject var deviceManager: DeviceManager
    @EnvironmentObject var themeManager: ThemeManager
    @State private var selectedTimeRange: TimeRange = .week
    @State private var selectedMetric: AnalyticsMetric = .battery
    @State private var showingExportSheet = false
    
    enum TimeRange: String, CaseIterable {
        case day = "24H"
        case week = "7D"
        case month = "30D"
        case year = "1Y"
        
        var displayName: String {
            switch self {
            case .day: return "24 Hours"
            case .week: return "7 Days"
            case .month: return "30 Days"
            case .year: return "1 Year"
            }
        }
    }
    
    enum AnalyticsMetric: String, CaseIterable {
        case battery = "Battery"
        case storage = "Storage"
        case performance = "Performance"
        case thermal = "Thermal"
        
        var icon: String {
            switch self {
            case .battery: return "battery.100"
            case .storage: return "internaldrive"
            case .performance: return "speedometer"
            case .thermal: return "thermometer"
            }
        }
        
        var color: Color {
            switch self {
            case .battery: return .green
            case .storage: return .blue
            case .performance: return .orange
            case .thermal: return .red
            }
        }
    }
    
    var body: some View {
        ScrollView {
            VStack(spacing: 24) {
                // Header
                headerSection
                
                // Time Range Selector
                timeRangeSelector
                
                // Main Chart
                mainChartSection
                
                // Metric Selector
                metricSelector
                
                // Insights Cards
                insightsSection
                
                // Trend Analysis
                trendAnalysisSection
            }
            .padding(.horizontal, 24)
            .padding(.bottom, 24)
        }
        .background(themeManager.currentTheme.primaryColor)
        .sheet(isPresented: $showingExportSheet) {
            ExportOptionsView()
        }
    }
    
    // MARK: - Header Section
    private var headerSection: some View {
        HStack {
            VStack(alignment: .leading, spacing: 4) {
                Text("Analytics")
                    .font(.title2)
                    .fontWeight(.bold)
                    .foregroundColor(themeManager.currentTheme.textPrimary)
                
                if let device = deviceManager.selectedDevice {
                    Text("Analyzing \(device.name)")
                        .font(.subheadline)
                        .foregroundColor(themeManager.currentTheme.textSecondary)
                } else {
                    Text("No device selected")
                        .font(.subheadline)
                        .foregroundColor(themeManager.currentTheme.textSecondary)
                }
            }
            
            Spacer()
            
            // Export Button
            Button(action: {
                showingExportSheet = true
            }) {
                HStack(spacing: 6) {
                    Image(systemName: "square.and.arrow.up")
                        .font(.system(size: 14, weight: .medium))
                    Text("Export")
                        .font(.system(size: 14, weight: .semibold))
                }
                .foregroundColor(themeManager.currentTheme.accentColor)
                .padding(.horizontal, 12)
                .padding(.vertical, 8)
                .background(
                    RoundedRectangle(cornerRadius: 8)
                        .fill(themeManager.currentTheme.accentColor.opacity(0.1))
                )
            }
            .buttonStyle(PlainButtonStyle())
        }
        .padding(.top, 24)
    }
    
    // MARK: - Time Range Selector
    private var timeRangeSelector: some View {
        HStack(spacing: 0) {
            ForEach(TimeRange.allCases, id: \.self) { range in
                Button(action: {
                    withAnimation(.easeInOut(duration: 0.2)) {
                        selectedTimeRange = range
                    }
                }) {
                    Text(range.rawValue)
                        .font(.system(size: 14, weight: .medium))
                        .foregroundColor(
                            selectedTimeRange == range ?
                            .white : themeManager.currentTheme.textSecondary
                        )
                        .padding(.horizontal, 16)
                        .padding(.vertical, 8)
                        .background(
                            RoundedRectangle(cornerRadius: 8)
                                .fill(
                                    selectedTimeRange == range ?
                                    themeManager.currentTheme.accentColor :
                                    Color.clear
                                )
                        )
                }
                .buttonStyle(PlainButtonStyle())
            }
        }
        .padding(4)
        .background(
            RoundedRectangle(cornerRadius: 12)
                .fill(themeManager.currentTheme.secondaryColor)
        )
    }
    
    // MARK: - Main Chart Section
    private var mainChartSection: some View {
        VStack(alignment: .leading, spacing: 16) {
            HStack {
                Text("\(selectedMetric.rawValue) Trend")
                    .font(.headline)
                    .fontWeight(.semibold)
                    .foregroundColor(themeManager.currentTheme.textPrimary)
                
                Spacer()
                
                Text(selectedTimeRange.displayName)
                    .font(.caption)
                    .foregroundColor(themeManager.currentTheme.textSecondary)
            }
            
            // Chart Container
            VStack(spacing: 12) {
                // Mock Chart - Replace with actual Chart implementation
                chartView
                
                // Chart Legend
                chartLegend
            }
            .padding(20)
            .background(
                RoundedRectangle(cornerRadius: 16)
                    .fill(themeManager.currentTheme.secondaryColor)
            )
        }
    }
    
    // MARK: - Chart View (Mock)
    private var chartView: some View {
        GeometryReader { geometry in
            ZStack {
                // Grid Lines
                VStack(spacing: 0) {
                    ForEach(0..<5) { _ in
                        Rectangle()
                            .fill(themeManager.currentTheme.textSecondary.opacity(0.1))
                            .frame(height: 1)
                        Spacer()
                    }
                }
                
                // Mock Chart Line
                Path { path in
                    let width = geometry.size.width
                    let height = geometry.size.height
                    let points = generateMockDataPoints(width: width, height: height)
                    
                    path.move(to: points[0])
                    for point in points.dropFirst() {
                        path.addLine(to: point)
                    }
                }
                .stroke(
                    LinearGradient(
                        colors: [selectedMetric.color, selectedMetric.color.opacity(0.6)],
                        startPoint: .leading,
                        endPoint: .trailing
                    ),
                    style: StrokeStyle(lineWidth: 3, lineCap: .round, lineJoin: .round)
                )
                
                // Data Points
                ForEach(0..<generateMockDataPoints(width: geometry.size.width, height: geometry.size.height).count, id: \.self) { index in
                    let points = generateMockDataPoints(width: geometry.size.width, height: geometry.size.height)
                    Circle()
                        .fill(selectedMetric.color)
                        .frame(width: 6, height: 6)
                        .position(points[index])
                }
            }
        }
        .frame(height: 200)
    }
    
    // MARK: - Chart Legend
    private var chartLegend: some View {
        HStack {
            HStack(spacing: 6) {
                Circle()
                    .fill(selectedMetric.color)
                    .frame(width: 8, height: 8)
                Text(selectedMetric.rawValue)
                    .font(.caption)
                    .foregroundColor(themeManager.currentTheme.textSecondary)
            }
            
            Spacer()
            
            // Current Value
            VStack(alignment: .trailing, spacing: 2) {
                Text("Current")
                    .font(.caption2)
                    .foregroundColor(themeManager.currentTheme.textSecondary)
                Text(currentValue)
                    .font(.caption)
                    .fontWeight(.semibold)
                    .foregroundColor(themeManager.currentTheme.textPrimary)
            }
        }
    }
    
    // MARK: - Metric Selector
    private var metricSelector: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Metrics")
                .font(.headline)
                .fontWeight(.semibold)
                .foregroundColor(themeManager.currentTheme.textPrimary)
            
            LazyVGrid(columns: [
                GridItem(.flexible()),
                GridItem(.flexible()),
                GridItem(.flexible()),
                GridItem(.flexible())
            ], spacing: 12) {
                ForEach(AnalyticsMetric.allCases, id: \.self) { metric in
                    MetricButton(
                        metric: metric,
                        isSelected: selectedMetric == metric
                    ) {
                        withAnimation(.easeInOut(duration: 0.2)) {
                            selectedMetric = metric
                        }
                    }
                }
            }
        }
    }
    
    // MARK: - Insights Section
    private var insightsSection: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("Insights")
                .font(.headline)
                .fontWeight(.semibold)
                .foregroundColor(themeManager.currentTheme.textPrimary)
            
            VStack(spacing: 12) {
                ForEach(generateInsights(), id: \.id) { insight in
                    InsightCard(insight: insight)
                }
            }
        }
    }
    
    // MARK: - Trend Analysis Section
    private var trendAnalysisSection: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("Trend Analysis")
                .font(.headline)
                .fontWeight(.semibold)
                .foregroundColor(themeManager.currentTheme.textPrimary)
            
            HStack(spacing: 16) {
                TrendCard(
                    title: "7-Day Average",
                    value: "87.2%",
                    trend: .up,
                    change: "+2.1%"
                )
                
                TrendCard(
                    title: "Peak Usage",
                    value: "94.8%",
                    trend: .stable,
                    change: "0.0%"
                )
                
                TrendCard(
                    title: "Lowest Point",
                    value: "23.1%",
                    trend: .down,
                    change: "-5.2%"
                )
            }
        }
    }
    
    // MARK: - Helper Methods
    private func generateMockDataPoints(width: CGFloat, height: CGFloat) -> [CGPoint] {
        let pointCount = 20
        var points: [CGPoint] = []
        
        for i in 0..<pointCount {
            let x = (width / CGFloat(pointCount - 1)) * CGFloat(i)
            let baseY = height * 0.5
            let variation = CGFloat.random(in: -height * 0.3...height * 0.3)
            let y = baseY + variation
            points.append(CGPoint(x: x, y: y))
        }
        
        return points
    }
    
    private var currentValue: String {
        switch selectedMetric {
        case .battery: return "87%"
        case .storage: return "48%"
        case .performance: return "92%"
        case .thermal: return "34°C"
        }
    }
    
    private func generateInsights() -> [AnalyticsInsight] {
        [
            AnalyticsInsight(
                title: "Battery Optimization",
                description: "Your battery performance improved by 8% after enabling optimized charging.",
                type: .positive,
                impact: "High"
            ),
            AnalyticsInsight(
                title: "Storage Warning",
                description: "Storage usage increased 15% this week. Consider cleaning cache files.",
                type: .warning,
                impact: "Medium"
            ),
            AnalyticsInsight(
                title: "Performance Stable",
                description: "Device performance remains consistent across all metrics.",
                type: .neutral,
                impact: "Low"
            )
        ]
    }
}

// MARK: - Metric Button
struct MetricButton: View {
    let metric: AnalyticsView.AnalyticsMetric
    let isSelected: Bool
    let action: () -> Void
    @EnvironmentObject var themeManager: ThemeManager
    
    var body: some View {
        Button(action: action) {
            VStack(spacing: 8) {
                Image(systemName: metric.icon)
                    .font(.system(size: 20, weight: .medium))
                    .foregroundColor(isSelected ? .white : metric.color)
                
                Text(metric.rawValue)
                    .font(.caption)
                    .fontWeight(.medium)
                    .foregroundColor(isSelected ? .white : themeManager.currentTheme.textPrimary)
            }
            .frame(maxWidth: .infinity)
            .padding(.vertical, 12)
            .background(
                RoundedRectangle(cornerRadius: 12)
                    .fill(isSelected ? metric.color : themeManager.currentTheme.secondaryColor)
                    .overlay(
                        RoundedRectangle(cornerRadius: 12)
                            .stroke(isSelected ? Color.clear : metric.color.opacity(0.3), lineWidth: 1)
                    )
            )
        }
        .buttonStyle(PlainButtonStyle())
    }
}

// MARK: - Insight Card
struct InsightCard: View {
    let insight: AnalyticsInsight
    @EnvironmentObject var themeManager: ThemeManager
    
    var body: some View {
        HStack(spacing: 12) {
            // Icon
            Image(systemName: insight.type.icon)
                .font(.system(size: 16, weight: .medium))
                .foregroundColor(insight.type.color)
                .frame(width: 24, height: 24)
            
            // Content
            VStack(alignment: .leading, spacing: 4) {
                Text(insight.title)
                    .font(.subheadline)
                    .fontWeight(.semibold)
                    .foregroundColor(themeManager.currentTheme.textPrimary)
                
                Text(insight.description)
                    .font(.caption)
                    .foregroundColor(themeManager.currentTheme.textSecondary)
                    .fixedSize(horizontal: false, vertical: true)
            }
            
            Spacer()
            
            // Impact Badge
            Text(insight.impact)
                .font(.caption2)
                .fontWeight(.medium)
                .foregroundColor(insight.type.color)
                .padding(.horizontal, 8)
                .padding(.vertical, 4)
                .background(
                    RoundedRectangle(cornerRadius: 8)
                        .fill(insight.type.color.opacity(0.1))
                )
        }
        .padding(16)
        .background(
            RoundedRectangle(cornerRadius: 12)
                .fill(themeManager.currentTheme.secondaryColor)
        )
    }
}

// MARK: - Trend Card
struct TrendCard: View {
    let title: String
    let value: String
    let trend: TrendDirection
    let change: String
    @EnvironmentObject var themeManager: ThemeManager
    
    enum TrendDirection {
        case up, down, stable
        
        var icon: String {
            switch self {
            case .up: return "arrow.up.right"
            case .down: return "arrow.down.right"
            case .stable: return "minus"
            }
        }
        
        var color: Color {
            switch self {
            case .up: return .green
            case .down: return .red
            case .stable: return .orange
            }
        }
    }
    
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(title)
                .font(.caption)
                .foregroundColor(themeManager.currentTheme.textSecondary)
            
            Text(value)
                .font(.title3)
                .fontWeight(.bold)
                .foregroundColor(themeManager.currentTheme.textPrimary)
            
            HStack(spacing: 4) {
                Image(systemName: trend.icon)
                    .font(.caption)
                    .foregroundColor(trend.color)
                
                Text(change)
                    .font(.caption)
                    .foregroundColor(trend.color)
            }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(16)
        .background(
            RoundedRectangle(cornerRadius: 12)
                .fill(themeManager.currentTheme.secondaryColor)
        )
    }
}

// MARK: - Analytics Models
struct AnalyticsInsight: Identifiable {
    let id = UUID()
    let title: String
    let description: String
    let type: InsightType
    let impact: String
    
    enum InsightType {
        case positive, warning, neutral
        
        var icon: String {
            switch self {
            case .positive: return "checkmark.circle.fill"
            case .warning: return "exclamationmark.triangle.fill"
            case .neutral: return "info.circle.fill"
            }
        }
        
        var color: Color {
            switch self {
            case .positive: return .green
            case .warning: return .orange
            case .neutral: return .blue
            }
        }
    }
}

// MARK: - Export Options View
struct ExportOptionsView: View {
    @EnvironmentObject var themeManager: ThemeManager
    @Environment(\.dismiss) private var dismiss
    
    var body: some View {
        NavigationView {
            VStack(spacing: 24) {
                Text("Export Analytics Data")
                    .font(.title2)
                    .fontWeight(.bold)
                    .foregroundColor(themeManager.currentTheme.textPrimary)
                
                VStack(spacing: 16) {
                    ExportOptionRow(
                        title: "PDF Report",
                        description: "Comprehensive analytics report",
                        icon: "doc.text"
                    ) {}
                    
                    ExportOptionRow(
                        title: "CSV Data",
                        description: "Raw data for external analysis",
                        icon: "tablecells"
                    ) {}
                    
                    ExportOptionRow(
                        title: "JSON Export",
                        description: "Machine-readable format",
                        icon: "doc.text.below.ecg"
                    ) {}
                }
                
                Spacer()
            }
            .padding(24)
            .background(themeManager.currentTheme.primaryColor)
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

// MARK: - Export Option Row
struct ExportOptionRow: View {
    let title: String
    let description: String
    let icon: String
    let action: () -> Void
    @EnvironmentObject var themeManager: ThemeManager
    
    var body: some View {
        Button(action: action) {
            HStack(spacing: 16) {
                Image(systemName: icon)
                    .font(.system(size: 20, weight: .medium))
                    .foregroundColor(themeManager.currentTheme.accentColor)
                    .frame(width: 32, height: 32)
                
                VStack(alignment: .leading, spacing: 4) {
                    Text(title)
                        .font(.subheadline)
                        .fontWeight(.semibold)
                        .foregroundColor(themeManager.currentTheme.textPrimary)
                    
                    Text(description)
                        .font(.caption)
                        .foregroundColor(themeManager.currentTheme.textSecondary)
                }
                
                Spacer()
                
                Image(systemName: "chevron.right")
                    .font(.caption)
                    .foregroundColor(themeManager.currentTheme.textSecondary)
            }
            .padding(16)
            .background(
                RoundedRectangle(cornerRadius: 12)
                    .fill(themeManager.currentTheme.secondaryColor)
            )
        }
        .buttonStyle(PlainButtonStyle())
    }
}