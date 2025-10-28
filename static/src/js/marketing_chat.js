/** @odoo-module **/

import { Component, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { rpc } from "@web/core/network/rpc";

export class MarketingChatBubble extends Component {
    setup() {
        this.state = useState({
            isOpen: false,
            messages: [
                { 
                    text: "Hello! I'm your marketing assistant. How can I help you today?", 
                    isBot: true, 
                    timestamp: new Date() 
                }
            ],
            inputValue: "",
            currentLanguage: 'en',
            isTyping: false
        });
    }

    get translations() {
        return {
            en: { 
                title: "Marketing Assistant", 
                placeholder: "Type your message...",
                welcome: "Hello! I'm your marketing assistant. How can I help you today?"
            },
            ar: { 
                title: "مساعد التسويق", 
                placeholder: "اكتب رسالتك...",
                welcome: "مرحباً! أنا مساعدك التسويقي. كيف يمكنني مساعدتك اليوم؟"
            }
        };
    }

    get t() {
        return this.translations[this.state.currentLanguage];
    }

    toggleChat() {
        this.state.isOpen = !this.state.isOpen;
    }

    closeChat() {
        this.state.isOpen = false;
    }

    toggleLanguage() {
        this.state.currentLanguage = this.state.currentLanguage === 'en' ? 'ar' : 'en';
        // Update welcome message
        this.state.messages = [{
            text: this.t.welcome,
            isBot: true,
            timestamp: new Date()
        }];
    }

    async sendMessage() {
        const message = this.state.inputValue.trim();
        if (!message) return;

        // Add user message
        this.state.messages.push({
            text: message,
            isBot: false,
            timestamp: new Date()
        });

        this.state.inputValue = "";
        this.state.isTyping = true;

        try {
            // Call backend service
            const response = await rpc("/ai_marketing_assistant/chat", {
                message: message,
                language: this.state.currentLanguage
            });

            setTimeout(() => {
                this.state.isTyping = false;
                this.state.messages.push({
                    text: response.response || "Thank you for your message!",
                    isBot: true,
                    timestamp: new Date()
                });
            }, 1000);

        } catch (error) {
            console.error("Chat error:", error);
            
            // Fallback responses
            const fallbackResponses = {
                en: {
                    greeting: "Hello! I'm here to help with your marketing needs.",
                    campaign: "I can help you analyze campaign performance and ROI.",
                    analytics: "Let me help you with marketing analytics and insights.",
                    default: "Thanks for your message! I'm here to help with marketing."
                },
                ar: {
                    greeting: "مرحباً! أنا هنا لمساعدتك في احتياجاتك التسويقية.",
                    campaign: "يمكنني مساعدتك في تحليل أداء الحملات والعائد على الاستثمار.",
                    analytics: "دعني أساعدك في تحليلات التسويق والرؤى.",
                    default: "شكراً لرسالتك! أنا هنا للمساعدة في التسويق."
                }
            };

            // Simple keyword detection for offline responses
            const messageLower = message.toLowerCase();
            let responseKey = 'default';
            
            if (messageLower.includes('hello') || messageLower.includes('hi') || 
                messageLower.includes('مرحبا') || messageLower.includes('أهلا')) {
                responseKey = 'greeting';
            } else if (messageLower.includes('campaign') || messageLower.includes('حملة')) {
                responseKey = 'campaign';
            } else if (messageLower.includes('analytics') || messageLower.includes('تحليل')) {
                responseKey = 'analytics';
            }

            this.state.isTyping = false;
            this.state.messages.push({
                text: fallbackResponses[this.state.currentLanguage][responseKey],
                isBot: true,
                timestamp: new Date()
            });
        }
    }

    onKeyPress(event) {
        if (event.key === 'Enter') {
            event.preventDefault();
            this.sendMessage();
        }
    }

    formatTime(timestamp) {
        return timestamp.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
    }
}

MarketingChatBubble.template = "ai_marketing_assistant.ChatBubble";

// Register as systray component
registry.category("systray").add("MarketingChatBubble", {
    Component: MarketingChatBubble,
});