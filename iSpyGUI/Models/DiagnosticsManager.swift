import SwiftUI
import Combine
import Foundation

// MARK: - Diagnostics Manager
class DiagnosticsManager: ObservableObject {
    @Published var modules: [DiagnosticModule] = []
    @Published var isRunning = false
    @Published var overallHealthScore: Double = 85.0
    @Published var criticalIssuesCount = 0
    @Published var lastUpdateTime = "Never"
    @Published var recentActivities: [ActivityItem] = []
    
    private let pythonInterface = PythonInterface()
    
    init() {
        setupModules()
        setupMockActivities()
    }
    
    // MARK: - Setup
    private func setupModules() {
        modules = [
            DiagnosticModule(
                name: "Battery Health",
                description: "Monitor battery performance and cycle count",
                icon: "battery.100",
                status: .good,
                score: 87.5,
                isRunning: false
            ),
            DiagnosticModule(
                name: "Storage Analysis",
                description: "Analyze storage usage and optimization",
                icon: "internaldrive",
                status: .excellent,
                score: 92.3,
                isRunning: false
            ),
            DiagnosticModule(
                name: "Network Diagnostics",
                description: "Check connectivity and network performance",
                icon: "wifi",
                status: .good,
                score: 78.9,
                isRunning: false
            ),
            DiagnosticModule(
                name: "App Management",
                description: "Analyze installed apps and permissions",
                icon: "app.badge",
                status: .warning,
                score: 65.4,
                isRunning: false
            ),
            DiagnosticModule(
                name: "Security Analysis",
                description: "Device security posture assessment",
                icon: "lock.shield",
                status: .excellent,
                score: 94.2,
                isRunning: false
            ),
            DiagnosticModule(
                name: "Performance",
                description: "CPU, memory, and thermal analysis",
                icon: "speedometer",
                status: .good,
                score: 81.7,
                isRunning: false
            ),
            DiagnosticModule(
                name: "Thermal Monitor",
                description: "Temperature tracking and overheating prevention",
                icon: "thermometer",
                status: .excellent,
                score: 96.1,
                isRunning: false
            ),
            DiagnosticModule(
                name: "Backup Status",
                description: "Backup configuration and data protection",
                icon: "externaldrive.connected.to.line.below",
                status: .critical,
                score: 32.8,
                isRunning: false
            ),
            DiagnosticModule(
                name: "Accessibility",
                description: "Accessibility features and configuration",
                icon: "accessibility",
                status: .good,
                score: 73.5,
                isRunning: false
            )
        ]
        
        updateOverallHealth()
    }
    
    private func setupMockActivities() {
        recentActivities = [
            ActivityItem(
                title: "Battery diagnostic completed",
                subtitle: "87% health score - Good condition",
                type: .success,
                timeAgo: "2 min ago"
            ),
            ActivityItem(
                title: "Storage analysis finished",
                subtitle: "Found 2.3 GB of cache files to clean",
                type: .info,
                timeAgo: "5 min ago"
            ),
            ActivityItem(
                title: "Critical backup issue detected",
                subtitle: "No recent backup found - immediate action needed",
                type: .warning,
                timeAgo: "12 min ago"
            ),
            ActivityItem(
                title: "Security scan completed",
                subtitle: "All security checks passed",
                type: .success,
                timeAgo: "18 min ago"
            ),
            ActivityItem(
                title: "Performance optimization suggested",
                subtitle: "Close 5 background apps to improve performance",
                type: .info,
                timeAgo: "25 min ago"
            )
        ]
    }
    
    // MARK: - Diagnostic Operations
    func runFullDiagnostic() {
        guard !isRunning else {
            stopDiagnostic()
            return
        }
        
        isRunning = true
        
        // Run diagnostics sequentially with animation
        runModuleDiagnostics()
    }
    
    private func runModuleDiagnostics() {
        var delay: Double = 0
        
        for (index, _) in modules.enumerated() {
            DispatchQueue.main.asyncAfter(deadline: .now() + delay) {
                withAnimation(.easeInOut(duration: 0.3)) {
                    self.modules[index].isRunning = true
                }
                
                // Simulate diagnostic running
                DispatchQueue.main.asyncAfter(deadline: .now() + 2.0 + Double.random(in: 0...1)) {
                    withAnimation(.easeInOut(duration: 0.3)) {
                        self.modules[index].isRunning = false
                        self.modules[index].score = Double.random(in: 30...100)
                        self.modules[index].status = self.statusForScore(self.modules[index].score)
                    }
                    
                    // Add activity
                    self.addActivity(for: self.modules[index])
                    
                    // Check if all modules are done
                    if !self.modules.contains(where: { $0.isRunning }) {
                        self.completeDiagnostic()
                    }
                }
            }
            
            delay += 0.5 // Stagger start times
        }
    }
    
    private func completeDiagnostic() {
        isRunning = false
        updateOverallHealth()
        lastUpdateTime = formatCurrentTime()
        
        // Add completion activity
        let activity = ActivityItem(
            title: "Full diagnostic completed",
            subtitle: "Health score: \(Int(overallHealthScore))/100",
            type: overallHealthScore > 80 ? .success : (overallHealthScore > 60 ? .info : .warning),
            timeAgo: "Just now"
        )
        
        withAnimation(.easeInOut(duration: 0.3)) {
            recentActivities.insert(activity, at: 0)
            if recentActivities.count > 10 {
                recentActivities.removeLast()
            }
        }
    }
    
    func stopDiagnostic() {
        isRunning = false
        
        for index in modules.indices {
            modules[index].isRunning = false
        }
    }
    
    func runSingleModule(_ module: DiagnosticModule) {
        guard let index = modules.firstIndex(where: { $0.id == module.id }) else { return }
        
        withAnimation(.easeInOut(duration: 0.3)) {
            modules[index].isRunning = true
        }
        
        // Simulate diagnostic
        DispatchQueue.main.asyncAfter(deadline: .now() + 3.0) {
            withAnimation(.easeInOut(duration: 0.3)) {
                self.modules[index].isRunning = false
                self.modules[index].score = Double.random(in: 30...100)
                self.modules[index].status = self.statusForScore(self.modules[index].score)
            }
            
            self.addActivity(for: self.modules[index])
            self.updateOverallHealth()
        }
    }
    
    // MARK: - Helper Methods
    private func updateOverallHealth() {
        let totalScore = modules.reduce(0) { $0 + $1.score }
        overallHealthScore = totalScore / Double(modules.count)
        
        criticalIssuesCount = modules.filter { $0.status == .critical }.count
    }
    
    private func statusForScore(_ score: Double) -> DiagnosticStatus {
        switch score {
        case 90...100: return .excellent
        case 70..<90: return .good
        case 50..<70: return .warning
        default: return .critical
        }
    }
    
    private func addActivity(for module: DiagnosticModule) {
        let activity = ActivityItem(
            title: "\(module.name) completed",
            subtitle: statusMessage(for: module),
            type: activityType(for: module.status),
            timeAgo: "Just now"
        )
        
        withAnimation(.easeInOut(duration: 0.3)) {
            recentActivities.insert(activity, at: 0)
            if recentActivities.count > 10 {
                recentActivities.removeLast()
            }
        }
    }
    
    private func statusMessage(for module: DiagnosticModule) -> String {
        let score = Int(module.score)
        switch module.status {
        case .excellent:
            return "Score: \(score)/100 - Excellent condition"
        case .good:
            return "Score: \(score)/100 - Good condition"
        case .warning:
            return "Score: \(score)/100 - Needs attention"
        case .critical:
            return "Score: \(score)/100 - Critical issues found"
        }
    }
    
    private func activityType(for status: DiagnosticStatus) -> ActivityType {
        switch status {
        case .excellent, .good: return .success
        case .warning: return .info
        case .critical: return .warning
        }
    }
    
    private func formatCurrentTime() -> String {
        let formatter = DateFormatter()
        formatter.dateStyle = .none
        formatter.timeStyle = .short
        return formatter.string(from: Date())
    }
}

// MARK: - Diagnostic Module Model
struct DiagnosticModule: Identifiable {
    let id = UUID()
    let name: String
    let description: String
    let icon: String
    var status: DiagnosticStatus
    var score: Double
    var isRunning: Bool
    
    var recommendations: [String] {
        switch status {
        case .excellent:
            return ["Device is performing optimally", "Continue current usage patterns"]
        case .good:
            return ["Minor optimizations recommended", "Regular monitoring advised"]
        case .warning:
            return ["Attention required", "Review settings and usage", "Consider optimization"]
        case .critical:
            return ["Immediate action needed", "Critical issues detected", "Contact support if needed"]
        }
    }
}

// MARK: - Diagnostic Status
enum DiagnosticStatus {
    case excellent, good, warning, critical
    
    var color: Color {
        switch self {
        case .excellent: return .green
        case .good: return .blue
        case .warning: return .orange
        case .critical: return .red
        }
    }
    
    var icon: String {
        switch self {
        case .excellent: return "checkmark.circle.fill"
        case .good: return "checkmark.circle"
        case .warning: return "exclamationmark.triangle.fill"
        case .critical: return "xmark.circle.fill"
        }
    }
}

// MARK: - Activity Item Model
struct ActivityItem: Identifiable {
    let id = UUID()
    let title: String
    let subtitle: String
    let type: ActivityType
    let timeAgo: String
}

// MARK: - Activity Type
enum ActivityType {
    case success, info, warning, error
    
    var color: Color {
        switch self {
        case .success: return .green
        case .info: return .blue
        case .warning: return .orange
        case .error: return .red
        }
    }
}