import SwiftUI

struct DevicesView: View {
    @EnvironmentObject var deviceManager: DeviceManager
    @EnvironmentObject var themeManager: ThemeManager
    @State private var showingDeviceDetail = false
    @State private var selectedDeviceForDetail: Device?
    
    var body: some View {
        VStack(spacing: 0) {
            // Header
            HStack {
                VStack(alignment: .leading, spacing: 4) {
                    Text("Connected Devices")
                        .font(.title2)
                        .fontWeight(.bold)
                        .foregroundColor(themeManager.currentTheme.textPrimary)
                    
                    Text("\(deviceManager.devices.count) device\(deviceManager.devices.count == 1 ? "" : "s") found")
                        .font(.subheadline)
                        .foregroundColor(themeManager.currentTheme.textSecondary)
                }
                
                Spacer()
                
                // Refresh Button
                Button(action: {
                    withAnimation(.spring()) {
                        deviceManager.refreshDevices()
                    }
                }) {
                    Image(systemName: "arrow.clockwise")
                        .font(.system(size: 16, weight: .medium))
                        .foregroundColor(themeManager.currentTheme.accentColor)
                        .rotationEffect(.degrees(deviceManager.isScanning ? 360 : 0))
                        .animation(
                            deviceManager.isScanning ? 
                            Animation.linear(duration: 1).repeatForever(autoreverses: false) : 
                            .default,
                            value: deviceManager.isScanning
                        )
                }
                .buttonStyle(PlainButtonStyle())
                .padding(8)
                .background(
                    RoundedRectangle(cornerRadius: 8)
                        .fill(themeManager.currentTheme.accentColor.opacity(0.1))
                )
            }
            .padding(.horizontal, 24)
            .padding(.top, 24)
            .padding(.bottom, 16)
            
            // Device List
            if deviceManager.devices.isEmpty {
                EmptyDevicesView()
            } else {
                ScrollView {
                    LazyVStack(spacing: 16) {
                        ForEach(deviceManager.devices) { device in
                            DeviceCard(device: device) {
                                deviceManager.selectDevice(device)
                            } onDetailTap: {
                                selectedDeviceForDetail = device
                                showingDeviceDetail = true
                            }
                        }
                    }
                    .padding(.horizontal, 24)
                    .padding(.bottom, 24)
                }
            }
        }
        .background(themeManager.currentTheme.primaryColor)
        .sheet(isPresented: $showingDeviceDetail) {
            if let device = selectedDeviceForDetail {
                DeviceDetailView(device: device)
            }
        }
    }
}

// MARK: - Device Card
struct DeviceCard: View {
    let device: Device
    let onSelect: () -> Void
    let onDetailTap: () -> Void
    @EnvironmentObject var deviceManager: DeviceManager
    @EnvironmentObject var themeManager: ThemeManager
    
    var body: some View {
        VStack(spacing: 16) {
            // Header
            HStack {
                // Device Icon
                VStack {
                    Image(systemName: deviceIcon)
                        .font(.system(size: 32, weight: .medium))
                        .foregroundColor(themeManager.currentTheme.accentColor)
                    
                    Circle()
                        .fill(device.isConnected ? Color.green : Color.red)
                        .frame(width: 8, height: 8)
                }
                
                VStack(alignment: .leading, spacing: 4) {
                    Text(device.name)
                        .font(.headline)
                        .fontWeight(.semibold)
                        .foregroundColor(themeManager.currentTheme.textPrimary)
                    
                    Text(device.model)
                        .font(.subheadline)
                        .foregroundColor(themeManager.currentTheme.textSecondary)
                    
                    Text("iOS \(device.version)")
                        .font(.caption)
                        .foregroundColor(themeManager.currentTheme.textSecondary)
                }
                
                Spacer()
                
                // Selection Indicator
                if deviceManager.selectedDevice?.id == device.id {
                    Image(systemName: "checkmark.circle.fill")
                        .font(.system(size: 20))
                        .foregroundColor(themeManager.currentTheme.accentColor)
                }
            }
            
            // Quick Stats
            HStack(spacing: 24) {
                // Battery
                VStack(alignment: .leading, spacing: 4) {
                    HStack(spacing: 4) {
                        Image(systemName: "battery.100")
                            .font(.caption)
                            .foregroundColor(device.batteryStatus.color)
                        Text("Battery")
                            .font(.caption)
                            .foregroundColor(themeManager.currentTheme.textSecondary)
                    }
                    
                    Text("\(device.batteryLevel)%")
                        .font(.title3)
                        .fontWeight(.semibold)
                        .foregroundColor(themeManager.currentTheme.textPrimary)
                }
                
                Divider()
                    .background(themeManager.currentTheme.textSecondary.opacity(0.3))
                
                // Storage
                VStack(alignment: .leading, spacing: 4) {
                    HStack(spacing: 4) {
                        Image(systemName: "internaldrive")
                            .font(.caption)
                            .foregroundColor(storageColor)
                        Text("Storage")
                            .font(.caption)
                            .foregroundColor(themeManager.currentTheme.textSecondary)
                    }
                    
                    Text("\(String(format: "%.1f", device.storagePercentage))%")
                        .font(.title3)
                        .fontWeight(.semibold)
                        .foregroundColor(themeManager.currentTheme.textPrimary)
                }
                
                Spacer()
            }
            
            // Progress Bars
            VStack(spacing: 8) {
                // Battery Progress
                HStack {
                    Text("Battery")
                        .font(.caption)
                        .foregroundColor(themeManager.currentTheme.textSecondary)
                    Spacer()
                    Text("\(device.batteryLevel)%")
                        .font(.caption)
                        .foregroundColor(themeManager.currentTheme.textSecondary)
                }
                
                ProgressView(value: Double(device.batteryLevel), total: 100)
                    .progressViewStyle(CustomProgressViewStyle(color: device.batteryStatus.color))
                
                // Storage Progress
                HStack {
                    Text("Storage")
                        .font(.caption)
                        .foregroundColor(themeManager.currentTheme.textSecondary)
                    Spacer()
                    Text("\(String(format: "%.1f", device.storageUsed)) GB of \(String(format: "%.0f", device.storageTotal)) GB")
                        .font(.caption)
                        .foregroundColor(themeManager.currentTheme.textSecondary)
                }
                
                ProgressView(value: device.storageUsed, total: device.storageTotal)
                    .progressViewStyle(CustomProgressViewStyle(color: storageColor))
            }
            
            // Action Buttons
            HStack(spacing: 12) {
                Button("Select Device") {
                    withAnimation(.spring()) {
                        onSelect()
                    }
                }
                .buttonStyle(PrimaryButtonStyle())
                .disabled(deviceManager.selectedDevice?.id == device.id)
                
                Button("View Details") {
                    onDetailTap()
                }
                .buttonStyle(SecondaryButtonStyle())
            }
        }
        .padding(20)
        .background(
            RoundedRectangle(cornerRadius: 16)
                .fill(themeManager.currentTheme.secondaryColor)
                .overlay(
                    RoundedRectangle(cornerRadius: 16)
                        .stroke(
                            deviceManager.selectedDevice?.id == device.id ? 
                            themeManager.currentTheme.accentColor : 
                            Color.clear,
                            lineWidth: 2
                        )
                )
        )
        .shadow(color: Color.black.opacity(0.1), radius: 8, x: 0, y: 2)
    }
    
    private var deviceIcon: String {
        if device.model.contains("iPad") {
            return "ipad"
        } else {
            return "iphone"
        }
    }
    
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

// MARK: - Empty Devices View
struct EmptyDevicesView: View {
    @EnvironmentObject var themeManager: ThemeManager
    
    var body: some View {
        VStack(spacing: 24) {
            Image(systemName: "iphone.slash")
                .font(.system(size: 64, weight: .light))
                .foregroundColor(themeManager.currentTheme.textSecondary.opacity(0.5))
            
            VStack(spacing: 8) {
                Text("No Devices Found")
                    .font(.title2)
                    .fontWeight(.semibold)
                    .foregroundColor(themeManager.currentTheme.textPrimary)
                
                Text("Connect your iOS device via USB and make sure to trust this computer")
                    .font(.body)
                    .foregroundColor(themeManager.currentTheme.textSecondary)
                    .multilineTextAlignment(.center)
                    .padding(.horizontal, 32)
            }
            
            VStack(spacing: 12) {
                HStack(spacing: 8) {
                    Image(systemName: "1.circle.fill")
                        .foregroundColor(themeManager.currentTheme.accentColor)
                    Text("Connect your device with a USB cable")
                        .font(.subheadline)
                        .foregroundColor(themeManager.currentTheme.textSecondary)
                    Spacer()
                }
                
                HStack(spacing: 8) {
                    Image(systemName: "2.circle.fill")
                        .foregroundColor(themeManager.currentTheme.accentColor)
                    Text("Tap 'Trust' when prompted on your device")
                        .font(.subheadline)
                        .foregroundColor(themeManager.currentTheme.textSecondary)
                    Spacer()
                }
                
                HStack(spacing: 8) {
                    Image(systemName: "3.circle.fill")
                        .foregroundColor(themeManager.currentTheme.accentColor)
                    Text("Device will appear here automatically")
                        .font(.subheadline)
                        .foregroundColor(themeManager.currentTheme.textSecondary)
                    Spacer()
                }
            }
            .padding(.horizontal, 32)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .padding(48)
    }
}

// MARK: - Custom Progress View Style
struct CustomProgressViewStyle: ProgressViewStyle {
    let color: Color
    @EnvironmentObject var themeManager: ThemeManager
    
    func makeBody(configuration: Configuration) -> some View {
        GeometryReader { geometry in
            ZStack(alignment: .leading) {
                Rectangle()
                    .fill(themeManager.currentTheme.textSecondary.opacity(0.2))
                    .frame(height: 6)
                    .cornerRadius(3)
                
                Rectangle()
                    .fill(color)
                    .frame(
                        width: CGFloat(configuration.fractionCompleted ?? 0) * geometry.size.width,
                        height: 6
                    )
                    .cornerRadius(3)
                    .animation(.easeInOut(duration: 0.3), value: configuration.fractionCompleted)
            }
        }
        .frame(height: 6)
    }
}

// MARK: - Button Styles
struct PrimaryButtonStyle: ButtonStyle {
    @EnvironmentObject var themeManager: ThemeManager
    
    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .font(.system(size: 14, weight: .semibold))
            .foregroundColor(.white)
            .padding(.horizontal, 16)
            .padding(.vertical, 8)
            .background(
                RoundedRectangle(cornerRadius: 8)
                    .fill(themeManager.currentTheme.accentColor)
                    .opacity(configuration.isPressed ? 0.8 : 1.0)
            )
            .scaleEffect(configuration.isPressed ? 0.98 : 1.0)
            .animation(.easeInOut(duration: 0.1), value: configuration.isPressed)
    }
}

struct SecondaryButtonStyle: ButtonStyle {
    @EnvironmentObject var themeManager: ThemeManager
    
    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .font(.system(size: 14, weight: .medium))
            .foregroundColor(themeManager.currentTheme.accentColor)
            .padding(.horizontal, 16)
            .padding(.vertical, 8)
            .background(
                RoundedRectangle(cornerRadius: 8)
                    .stroke(themeManager.currentTheme.accentColor, lineWidth: 1)
                    .background(
                        RoundedRectangle(cornerRadius: 8)
                            .fill(themeManager.currentTheme.accentColor.opacity(0.1))
                    )
            )
            .scaleEffect(configuration.isPressed ? 0.98 : 1.0)
            .animation(.easeInOut(duration: 0.1), value: configuration.isPressed)
    }
}