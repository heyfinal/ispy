import SwiftUI

struct AIAssistantView: View {
    @EnvironmentObject var aiManager: AIManager
    @EnvironmentObject var themeManager: ThemeManager
    @State private var messageText = ""
    @State private var isTyping = false
    @FocusState private var isTextFieldFocused: Bool
    
    var body: some View {
        VStack(spacing: 0) {
            // Header
            headerSection
            
            // Chat Messages
            chatSection
            
            // Input Section
            inputSection
        }
        .background(themeManager.currentTheme.primaryColor)
        .onAppear {
            if aiManager.messages.isEmpty {
                aiManager.addWelcomeMessage()
            }
        }
    }
    
    // MARK: - Header Section
    private var headerSection: some View {
        VStack(spacing: 16) {
            HStack {
                VStack(alignment: .leading, spacing: 4) {
                    Text("AI Assistant")
                        .font(.title2)
                        .fontWeight(.bold)
                        .foregroundColor(themeManager.currentTheme.textPrimary)
                    
                    HStack(spacing: 6) {
                        Circle()
                            .fill(aiManager.isOnline ? Color.green : Color.red)
                            .frame(width: 8, height: 8)
                        
                        Text(aiManager.isOnline ? "AI Assistant Online" : "AI Assistant Offline")
                            .font(.caption)
                            .foregroundColor(themeManager.currentTheme.textSecondary)
                    }
                }
                
                Spacer()
                
                // Clear Chat Button
                Button(action: {
                    withAnimation(.easeInOut(duration: 0.3)) {
                        aiManager.clearChat()
                    }
                }) {
                    Image(systemName: "trash")
                        .font(.system(size: 16, weight: .medium))
                        .foregroundColor(themeManager.currentTheme.textSecondary)
                        .padding(8)
                        .background(
                            RoundedRectangle(cornerRadius: 8)
                                .fill(themeManager.currentTheme.secondaryColor)
                        )
                }
                .buttonStyle(PlainButtonStyle())
            }
            
            // Quick Actions
            quickActionsSection
        }
        .padding(.horizontal, 24)
        .padding(.top, 24)
        .padding(.bottom, 16)
    }
    
    // MARK: - Quick Actions
    private var quickActionsSection: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: 12) {
                ForEach(aiManager.quickActions, id: \.self) { action in
                    QuickActionButton(title: action) {
                        messageText = action
                        sendMessage()
                    }
                }
            }
            .padding(.horizontal, 24)
        }
    }
    
    // MARK: - Chat Section
    private var chatSection: some View {
        ScrollViewReader { proxy in
            ScrollView {
                LazyVStack(spacing: 16) {
                    ForEach(aiManager.messages) { message in
                        ChatMessageView(message: message)
                            .id(message.id)
                    }
                    
                    if aiManager.isProcessing {
                        TypingIndicatorView()
                            .id("typing")
                    }
                }
                .padding(.horizontal, 24)
                .padding(.vertical, 16)
            }
            .onChange(of: aiManager.messages.count) { _ in
                withAnimation(.easeInOut(duration: 0.3)) {
                    if let lastMessage = aiManager.messages.last {
                        proxy.scrollTo(lastMessage.id, anchor: .bottom)
                    }
                }
            }
            .onChange(of: aiManager.isProcessing) { isProcessing in
                if isProcessing {
                    withAnimation(.easeInOut(duration: 0.3)) {
                        proxy.scrollTo("typing", anchor: .bottom)
                    }
                }
            }
        }
    }
    
    // MARK: - Input Section
    private var inputSection: some View {
        VStack(spacing: 12) {
            Divider()
                .background(themeManager.currentTheme.textSecondary.opacity(0.2))
            
            HStack(spacing: 12) {
                // Text Input
                TextField("Ask about your device...", text: $messageText, axis: .vertical)
                    .textFieldStyle(PlainTextFieldStyle())
                    .font(.body)
                    .foregroundColor(themeManager.currentTheme.textPrimary)
                    .padding(.horizontal, 16)
                    .padding(.vertical, 12)
                    .background(
                        RoundedRectangle(cornerRadius: 20)
                            .fill(themeManager.currentTheme.secondaryColor)
                            .overlay(
                                RoundedRectangle(cornerRadius: 20)
                                    .stroke(isTextFieldFocused ? themeManager.currentTheme.accentColor : Color.clear, lineWidth: 1)
                            )
                    )
                    .focused($isTextFieldFocused)
                    .onSubmit {
                        sendMessage()
                    }
                
                // Send Button
                Button(action: sendMessage) {
                    Image(systemName: aiManager.isProcessing ? "stop.circle.fill" : "arrow.up.circle.fill")
                        .font(.system(size: 24, weight: .medium))
                        .foregroundColor(messageText.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty && !aiManager.isProcessing ? 
                                       themeManager.currentTheme.textSecondary : 
                                       themeManager.currentTheme.accentColor)
                        .rotationEffect(.degrees(aiManager.isProcessing ? 0 : 0))
                        .animation(.easeInOut(duration: 0.2), value: aiManager.isProcessing)
                }
                .buttonStyle(PlainButtonStyle())
                .disabled(messageText.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty && !aiManager.isProcessing)
            }
            .padding(.horizontal, 24)
            .padding(.bottom, 24)
        }
        .background(themeManager.currentTheme.primaryColor)
    }
    
    // MARK: - Helper Methods
    private func sendMessage() {
        let trimmedMessage = messageText.trimmingCharacters(in: .whitespacesAndNewlines)
        
        if aiManager.isProcessing {
            aiManager.stopProcessing()
            return
        }
        
        guard !trimmedMessage.isEmpty else { return }
        
        aiManager.sendMessage(trimmedMessage)
        messageText = ""
        isTextFieldFocused = false
    }
}

// MARK: - Quick Action Button
struct QuickActionButton: View {
    let title: String
    let action: () -> Void
    @EnvironmentObject var themeManager: ThemeManager
    
    var body: some View {
        Button(action: action) {
            Text(title)
                .font(.caption)
                .foregroundColor(themeManager.currentTheme.textPrimary)
                .padding(.horizontal, 12)
                .padding(.vertical, 6)
                .background(
                    RoundedRectangle(cornerRadius: 16)
                        .fill(themeManager.currentTheme.secondaryColor)
                        .overlay(
                            RoundedRectangle(cornerRadius: 16)
                                .stroke(themeManager.currentTheme.accentColor.opacity(0.3), lineWidth: 1)
                        )
                )
        }
        .buttonStyle(PlainButtonStyle())
    }
}

// MARK: - Chat Message View
struct ChatMessageView: View {
    let message: ChatMessage
    @EnvironmentObject var themeManager: ThemeManager
    
    var body: some View {
        HStack(alignment: .top, spacing: 12) {
            if message.isFromUser {
                Spacer(minLength: 60)
                
                messageContent
                    .background(
                        RoundedRectangle(cornerRadius: 16)
                            .fill(themeManager.currentTheme.accentColor)
                    )
                
                // User Avatar
                Circle()
                    .fill(themeManager.currentTheme.accentColor.opacity(0.2))
                    .frame(width: 32, height: 32)
                    .overlay(
                        Image(systemName: "person.fill")
                            .font(.system(size: 14, weight: .medium))
                            .foregroundColor(themeManager.currentTheme.accentColor)
                    )
            } else {
                // AI Avatar
                Circle()
                    .fill(themeManager.currentTheme.secondaryColor)
                    .frame(width: 32, height: 32)
                    .overlay(
                        Image(systemName: "brain.head.profile")
                            .font(.system(size: 14, weight: .medium))
                            .foregroundColor(themeManager.currentTheme.accentColor)
                    )
                
                messageContent
                    .background(
                        RoundedRectangle(cornerRadius: 16)
                            .fill(themeManager.currentTheme.secondaryColor)
                    )
                
                Spacer(minLength: 60)
            }
        }
        .animation(.easeInOut(duration: 0.3), value: message.id)
    }
    
    private var messageContent: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(message.content)
                .font(.body)
                .foregroundColor(message.isFromUser ? .white : themeManager.currentTheme.textPrimary)
                .fixedSize(horizontal: false, vertical: true)
            
            // Timestamp
            HStack {
                Spacer()
                Text(message.timestamp)
                    .font(.caption2)
                    .foregroundColor(message.isFromUser ? .white.opacity(0.7) : themeManager.currentTheme.textSecondary)
            }
        }
        .padding(.horizontal, 16)
        .padding(.vertical, 12)
    }
}

// MARK: - Typing Indicator
struct TypingIndicatorView: View {
    @EnvironmentObject var themeManager: ThemeManager
    @State private var animationPhase = 0
    
    var body: some View {
        HStack(alignment: .top, spacing: 12) {
            // AI Avatar
            Circle()
                .fill(themeManager.currentTheme.secondaryColor)
                .frame(width: 32, height: 32)
                .overlay(
                    Image(systemName: "brain.head.profile")
                        .font(.system(size: 14, weight: .medium))
                        .foregroundColor(themeManager.currentTheme.accentColor)
                )
            
            // Typing Animation
            HStack(spacing: 4) {
                ForEach(0..<3) { index in
                    Circle()
                        .fill(themeManager.currentTheme.textSecondary.opacity(0.6))
                        .frame(width: 6, height: 6)
                        .scaleEffect(animationPhase == index ? 1.2 : 0.8)
                        .opacity(animationPhase == index ? 1.0 : 0.4)
                }
            }
            .padding(.horizontal, 16)
            .padding(.vertical, 12)
            .background(
                RoundedRectangle(cornerRadius: 16)
                    .fill(themeManager.currentTheme.secondaryColor)
            )
            .onAppear {
                withAnimation(.linear(duration: 0.6).repeatForever(autoreverses: false)) {
                    animationPhase = 2
                }
            }
            
            Spacer(minLength: 60)
        }
    }
}

// MARK: - AI Manager
class AIManager: ObservableObject {
    @Published var messages: [ChatMessage] = []
    @Published var isProcessing = false
    @Published var isOnline = true
    
    let quickActions = [
        "Check battery health",
        "Analyze storage usage",
        "Run security scan",
        "Optimize performance",
        "Check for issues"
    ]
    
    func addWelcomeMessage() {
        let welcomeMessage = ChatMessage(
            content: "Hello! I'm your AI diagnostic assistant. I can help you understand your device's health, troubleshoot issues, and provide optimization recommendations. What would you like to know about your device?",
            isFromUser: false,
            timestamp: formatTime(Date())
        )
        
        withAnimation(.easeInOut(duration: 0.3)) {
            messages.append(welcomeMessage)
        }
    }
    
    func sendMessage(_ content: String) {
        // Add user message
        let userMessage = ChatMessage(
            content: content,
            isFromUser: true,
            timestamp: formatTime(Date())
        )
        
        withAnimation(.easeInOut(duration: 0.3)) {
            messages.append(userMessage)
        }
        
        // Start processing
        isProcessing = true
        
        // Simulate AI response
        DispatchQueue.main.asyncAfter(deadline: .now() + Double.random(in: 1.5...3.0)) {
            self.generateAIResponse(for: content)
        }
    }
    
    private func generateAIResponse(for userMessage: String) {
        let response = generateResponse(for: userMessage)
        
        let aiMessage = ChatMessage(
            content: response,
            isFromUser: false,
            timestamp: formatTime(Date())
        )
        
        withAnimation(.easeInOut(duration: 0.3)) {
            self.messages.append(aiMessage)
            self.isProcessing = false
        }
    }
    
    private func generateResponse(for message: String) -> String {
        let lowercased = message.lowercased()
        
        if lowercased.contains("battery") {
            return "Based on your device's current battery analysis, your battery health is at 87%. This is considered good condition. Your battery has completed approximately 245 charge cycles. To maintain battery health, I recommend enabling Optimized Battery Charging and avoiding extreme temperatures."
        } else if lowercased.contains("storage") {
            return "Your device is using 245.6 GB of 512 GB total storage (48% used). I've identified several optimization opportunities: 2.3 GB of cache files can be cleared, and there are 15 unused apps that could be removed to free up 8.7 GB. Would you like me to guide you through the cleanup process?"
        } else if lowercased.contains("security") {
            return "Security scan completed! Your device has a strong security posture with a score of 94/100. All security features are properly configured: Face ID is enabled, device passcode is set, and all apps have appropriate permissions. No security vulnerabilities detected."
        } else if lowercased.contains("performance") {
            return "Performance analysis shows your device is running well with minor optimization opportunities. CPU usage is normal, but I've detected 5 background apps that could be closed to improve performance. Memory usage is at 78% - consider restarting the device if you experience slowdowns."
        } else if lowercased.contains("issue") || lowercased.contains("problem") {
            return "I've scanned your device and found 1 critical issue that needs attention: No recent backup detected. Your last backup was 12 days ago. I also found 3 minor issues: cache files need cleaning, 2 apps need updates, and background app refresh is enabled for 23 apps. Would you like detailed solutions for these issues?"
        } else {
            return "I understand you're asking about device diagnostics. I can help you with battery health analysis, storage optimization, security assessments, performance tuning, and troubleshooting issues. Could you be more specific about what aspect of your device you'd like me to analyze?"
        }
    }
    
    func stopProcessing() {
        isProcessing = false
    }
    
    func clearChat() {
        messages.removeAll()
        addWelcomeMessage()
    }
    
    private func formatTime(_ date: Date) -> String {
        let formatter = DateFormatter()
        formatter.timeStyle = .short
        return formatter.string(from: date)
    }
}

// MARK: - Chat Message Model
struct ChatMessage: Identifiable {
    let id = UUID()
    let content: String
    let isFromUser: Bool
    let timestamp: String
}