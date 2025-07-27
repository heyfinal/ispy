import SwiftUI
import Combine
import Foundation

// MARK: - Device Model
struct Device: Identifiable, Hashable {
    let id = UUID()
    let udid: String
    let name: String
    let model: String
    let version: String
    let batteryLevel: Int
    let storageUsed: Double
    let storageTotal: Double
    let isConnected: Bool
    
    var storagePercentage: Double {
        return (storageUsed / storageTotal) * 100
    }
    
    var batteryStatus: BatteryStatus {
        switch batteryLevel {
        case 0..<20: return .critical
        case 20..<50: return .low
        case 50..<80: return .good
        default: return .excellent
        }
    }
    
    enum BatteryStatus {
        case critical, low, good, excellent
        
        var color: Color {
            switch self {
            case .critical: return .red
            case .low: return .orange
            case .good: return .yellow
            case .excellent: return .green
            }
        }
    }
}

// MARK: - Device Manager
class DeviceManager: ObservableObject {
    @Published var devices: [Device] = []
    @Published var selectedDevice: Device?
    @Published var isScanning = false
    @Published var isConnected = false
    
    private var scanTimer: Timer?
    private let pythonInterface = PythonInterface()
    
    init() {
        startDeviceScanning()
        setupMockData() // For demo purposes
    }
    
    deinit {
        scanTimer?.invalidate()
    }
    
    // MARK: - Device Management
    func startDeviceScanning() {
        isScanning = true
        scanTimer = Timer.scheduledTimer(withTimeInterval: 5.0, repeats: true) { _ in
            self.scanForDevices()
        }
        scanForDevices() // Initial scan
    }
    
    func stopDeviceScanning() {
        isScanning = false
        scanTimer?.invalidate()
        scanTimer = nil
    }
    
    private func scanForDevices() {
        // In real implementation, this would call the Python backend
        pythonInterface.getConnectedDevices { [weak self] devices in
            DispatchQueue.main.async {
                self?.devices = devices
                self?.isConnected = !devices.isEmpty
                
                // Auto-select first device if none selected
                if self?.selectedDevice == nil, let firstDevice = devices.first {
                    self?.selectedDevice = firstDevice
                }
            }
        }
    }
    
    func selectDevice(_ device: Device) {
        selectedDevice = device
    }
    
    func refreshDevices() {
        scanForDevices()
    }
    
    // MARK: - Mock Data Setup
    private func setupMockData() {
        // Mock devices for demo
        let mockDevices = [
            Device(
                udid: "12345678-1234-1234-1234-123456789012",
                name: "Daniel's iPhone",
                model: "iPhone 15 Pro",
                version: "17.2.1",
                batteryLevel: 87,
                storageUsed: 245.6,
                storageTotal: 512.0,
                isConnected: true
            ),
            Device(
                udid: "87654321-4321-4321-4321-210987654321",
                name: "iPad Pro",
                model: "iPad Pro 12.9\"",
                version: "17.2",
                batteryLevel: 65,
                storageUsed: 128.3,
                storageTotal: 256.0,
                isConnected: true
            )
        ]
        
        self.devices = mockDevices
        self.selectedDevice = mockDevices.first
        self.isConnected = true
    }
}

// MARK: - Python Interface
class PythonInterface {
    func getConnectedDevices(completion: @escaping ([Device]) -> Void) {
        // This would interface with the Python backend
        // For now, return mock data
        DispatchQueue.global().asyncAfter(deadline: .now() + 0.5) {
            let devices = [
                Device(
                    udid: "12345678-1234-1234-1234-123456789012",
                    name: "Daniel's iPhone",
                    model: "iPhone 15 Pro",
                    version: "17.2.1",
                    batteryLevel: Int.random(in: 60...100),
                    storageUsed: Double.random(in: 200...300),
                    storageTotal: 512.0,
                    isConnected: true
                )
            ]
            completion(devices)
        }
    }
    
    func runDiagnostic(deviceUDID: String, module: String, completion: @escaping (DiagnosticResult) -> Void) {
        // Interface with Python backend
        DispatchQueue.global().asyncAfter(deadline: .now() + 2.0) {
            let result = DiagnosticResult.mockResult(for: module)
            completion(result)
        }
    }
}

// MARK: - Diagnostic Result Model
struct DiagnosticResult: Identifiable {
    let id = UUID()
    let module: String
    let status: Status
    let score: Double
    let recommendations: [String]
    let details: [String: Any]
    let timestamp: Date
    
    enum Status {
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
    
    static func mockResult(for module: String) -> DiagnosticResult {
        let statuses: [Status] = [.excellent, .good, .warning, .critical]
        let randomStatus = statuses.randomElement() ?? .good
        
        return DiagnosticResult(
            module: module,
            status: randomStatus,
            score: Double.random(in: 0...100),
            recommendations: [
                "Enable optimized battery charging",
                "Clear cache files to free up space",
                "Update to latest iOS version"
            ],
            details: [:],
            timestamp: Date()
        )
    }
}