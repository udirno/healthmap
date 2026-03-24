'use client';

import { useState, useMemo, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import { X, Send, Brain, Loader2, Sparkles, TrendingUp, TrendingDown, AlertTriangle } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { apiClient, Anomaly, TimeSeriesData } from '@/lib/api-client';

interface AIInsightPanelProps {
  selectedDisease: string;
  selectedRegion: string;
  dateRange: { start: string; end: string };
  onClose: () => void;
}

interface Message {
  role: 'user' | 'assistant';
  content: string;
  visualizationData?: {
    time_series: TimeSeriesData[];
    chart_type: string;
  };
  anomalies?: Anomaly[];
  trendData?: {
    growth_rate_pct: number;
    current_7day_avg: number;
    trend: string;
  };
}

export default function AIInsightPanel({
  selectedDisease,
  selectedRegion,
  dateRange,
  onClose,
}: AIInsightPanelProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content: `I'm ready to help you analyze ${selectedDisease} patterns in ${selectedRegion}. Ask me about trends, correlations, or comparisons.`,
    },
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  // Reset conversation when region or disease changes
  useEffect(() => {
    setMessages([
      {
        role: 'assistant',
        content: `I'm ready to help you analyze ${selectedDisease} patterns in ${selectedRegion}. Ask me about trends, correlations, or comparisons.`,
      },
    ]);
  }, [selectedRegion, selectedDisease]);

  // Generate contextual suggested questions
  const suggestedQuestions = useMemo(() => {
    const questions = [
      `What are the main trends for ${selectedDisease} in ${selectedRegion}?`,
      `How does climate correlate with ${selectedDisease} spread?`,
      `Compare USA vs India`,
      `What socioeconomic factors affect outcomes?`,
    ];

    // Show different suggestions if conversation has started
    if (messages.length > 1) {
      return [
        `Compare ${selectedRegion} to another region`,
        `What might explain these patterns?`,
        `How has this changed over time?`,
        `What are the key contributing factors?`,
      ];
    }

    return questions;
  }, [selectedDisease, selectedRegion, messages.length]);

  // Detect if question is a comparison query and extract regions
  const detectComparisonQuery = (question: string): string[] | null => {
    const lowerQuestion = question.toLowerCase();

    // Common comparison patterns
    const comparisonPatterns = [
      /compare\s+(.+?)\s+(?:vs|versus|and|to|with)\s+(.+?)(?:\s|$|\.|\?)/i,
      /(.+?)\s+(?:vs|versus)\s+(.+?)(?:\s|$|\.|\?)/i,
    ];

    for (const pattern of comparisonPatterns) {
      const match = question.match(pattern);
      if (match) {
        // Extract potential region names
        const region1 = match[1].trim();
        const region2 = match[2].trim();

        // Try to map region names to codes (simplified - you could make this more robust)
        const regionMap: Record<string, string> = {
          'usa': 'USA',
          'united states': 'USA',
          'india': 'IND',
          'china': 'CHN',
          'brazil': 'BRA',
          'uk': 'GBR',
          'united kingdom': 'GBR',
          'germany': 'DEU',
          'france': 'FRA',
          'italy': 'ITA',
          'spain': 'ESP',
          'canada': 'CAN',
          'japan': 'JPN',
          'south korea': 'KOR',
          'australia': 'AUS',
        };

        const code1 = regionMap[region1.toLowerCase()];
        const code2 = regionMap[region2.toLowerCase()];

        if (code1 && code2) {
          return [code1, code2];
        }
      }
    }

    return null;
  };

  const handleSuggestedQuestion = (question: string) => {
    setInput(question);
    // Auto-send the question
    setTimeout(() => handleSend(), 100);
  };

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage = input.trim();
    setInput('');

    // Add user message to local state
    const newMessages = [...messages, { role: 'user', content: userMessage }];
    setMessages(newMessages as Message[]);
    setIsLoading(true);

    try {
      // Build conversation history (exclude the welcome message and current question)
      const conversationHistory = newMessages
        .slice(1, -1) // Skip welcome message and current question
        .map(msg => ({ role: msg.role, content: msg.content }));

      // Check if this is a comparison query
      const comparisonRegions = detectComparisonQuery(userMessage);

      // Call real backend API with full context including conversation history
      const response = await apiClient.generateInsight({
        question: userMessage,
        disease: selectedDisease,
        region: comparisonRegions ? undefined : selectedRegion,
        regions: comparisonRegions || undefined,
        start_date: dateRange.start,
        end_date: dateRange.end,
        conversation_history: conversationHistory.length > 0 ? conversationHistory : undefined,
      });

      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: response.narrative,
          visualizationData: response.visualization_data,
          anomalies: response.anomalies,
          trendData: response.trend_data,
        },
      ]);
    } catch (error) {
      console.error('Error generating insight:', error);
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: 'Sorry, I encountered an error generating that insight. Please try again.',
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="h-full bg-[#1e293b] rounded-xl overflow-hidden border border-slate-700 flex flex-col">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 to-purple-700 p-4 flex items-center gap-3 border-b border-purple-800">
        <div className="w-9 h-9 bg-white/20 rounded-lg flex items-center justify-center">
          <Brain className="w-5 h-5 text-white" />
        </div>
        <div>
          <h2 className="font-bold text-white">AI Insights</h2>
          <p className="text-xs text-purple-200">Powered by Claude</p>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message, index) => (
          <div key={index} className="space-y-3">
            <div
              className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[85%] p-3 rounded-lg ${
                  message.role === 'user'
                    ? 'bg-blue-600 text-white'
                    : 'bg-slate-800/60 text-slate-100 border border-slate-700'
                }`}
              >
                <div className="text-sm leading-relaxed prose prose-invert prose-sm max-w-none prose-p:my-1 prose-headings:my-2 prose-ul:my-1 prose-ol:my-1 prose-li:my-0.5">
                  <ReactMarkdown>{message.content}</ReactMarkdown>
                </div>
              </div>
            </div>

            {/* Trend Alert */}
            {message.role === 'assistant' && message.trendData && (
              <div className={`flex justify-start`}>
                <div className={`max-w-[85%] p-3 rounded-lg border ${
                  message.trendData.trend === 'increasing'
                    ? 'bg-red-500/10 border-red-500/30'
                    : message.trendData.trend === 'decreasing'
                    ? 'bg-green-500/10 border-green-500/30'
                    : 'bg-blue-500/10 border-blue-500/30'
                }`}>
                  <div className="flex items-center gap-2 mb-1">
                    {message.trendData.trend === 'increasing' ? (
                      <TrendingUp className="w-4 h-4 text-red-400" />
                    ) : message.trendData.trend === 'decreasing' ? (
                      <TrendingDown className="w-4 h-4 text-green-400" />
                    ) : (
                      <TrendingUp className="w-4 h-4 text-blue-400" />
                    )}
                    <span className="text-xs font-semibold text-slate-200">
                      7-Day Trend: {message.trendData.growth_rate_pct > 0 ? '+' : ''}{message.trendData.growth_rate_pct}%
                    </span>
                  </div>
                  <p className="text-xs text-slate-400">
                    Current avg: {Math.round(message.trendData.current_7day_avg)} cases/day
                  </p>
                </div>
              </div>
            )}

            {/* Anomaly Alerts */}
            {message.role === 'assistant' && message.anomalies && message.anomalies.length > 0 && (
              <div className="flex justify-start">
                <div className="max-w-[85%] space-y-2">
                  <div className="flex items-center gap-2 text-xs text-slate-400 mb-2">
                    <AlertTriangle className="w-3.5 h-3.5 text-orange-400" />
                    <span className="font-medium">{message.anomalies.length} anomal{message.anomalies.length === 1 ? 'y' : 'ies'} detected</span>
                  </div>
                  {message.anomalies.slice(0, 3).map((anomaly, idx) => (
                    <div
                      key={idx}
                      className={`p-2.5 rounded-lg text-xs border ${
                        anomaly.severity === 'high'
                          ? 'bg-red-500/10 border-red-500/30'
                          : 'bg-orange-500/10 border-orange-500/30'
                      }`}
                    >
                      <div className="flex items-center justify-between mb-1">
                        <span className="font-semibold text-slate-200">
                          {anomaly.type === 'spike' ? '📈' : '📉'} {anomaly.date}
                        </span>
                        <span className={`text-xs font-semibold ${anomaly.severity === 'high' ? 'text-red-400' : 'text-orange-400'}`}>
                          {anomaly.deviation_pct > 0 ? '+' : ''}{anomaly.deviation_pct}%
                        </span>
                      </div>
                      <p className="text-slate-400">
                        {anomaly.value.toLocaleString()} cases ({anomaly.type})
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Visualization */}
            {message.role === 'assistant' && message.visualizationData && message.visualizationData.time_series && (
              <div className="flex justify-start">
                <div className="max-w-[100%] w-full bg-slate-800/40 border border-slate-700 p-3 rounded-lg">
                  <h4 className="text-xs font-semibold text-slate-200 mb-3">Case Trends Over Time</h4>
                  <ResponsiveContainer width="100%" height={200}>
                    <LineChart data={message.visualizationData.time_series}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                      <XAxis
                        dataKey="date"
                        tick={{ fontSize: 10, fill: '#94a3b8' }}
                        tickFormatter={(date) => new Date(date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                      />
                      <YAxis tick={{ fontSize: 10, fill: '#94a3b8' }} />
                      <Tooltip
                        contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #475569', borderRadius: '8px' }}
                        labelStyle={{ color: '#e2e8f0', fontSize: 11, fontWeight: 600 }}
                        itemStyle={{ fontSize: 11, color: '#cbd5e1' }}
                      />
                      <Legend wrapperStyle={{ fontSize: 11 }} />
                      <Line
                        type="monotone"
                        dataKey="new_cases"
                        stroke="#3b82f6"
                        strokeWidth={2}
                        name="New Cases"
                        dot={false}
                      />
                      <Line
                        type="monotone"
                        dataKey="new_deaths"
                        stroke="#f59e0b"
                        strokeWidth={2}
                        name="New Deaths"
                        dot={false}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </div>
            )}
          </div>
        ))}
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-slate-800/40 border border-slate-700 p-3 rounded-lg">
              <Loader2 className="w-5 h-5 text-purple-400 animate-spin" />
            </div>
          </div>
        )}
      </div>

      {/* Suggested Questions */}
      {!isLoading && messages.length <= 3 && (
        <div className="px-4 py-3 border-t border-slate-700 bg-slate-800/30">
          <div className="flex items-center gap-2 mb-2">
            <Sparkles className="w-3.5 h-3.5 text-purple-400" />
            <span className="text-xs font-semibold text-slate-300">Suggested questions</span>
          </div>
          <div className="flex flex-wrap gap-2">
            {suggestedQuestions.map((question, idx) => (
              <button
                key={idx}
                onClick={() => handleSuggestedQuestion(question)}
                className="text-xs px-3 py-1.5 rounded-full bg-slate-700/50 hover:bg-purple-600/30 text-slate-300 hover:text-purple-300 transition-all border border-slate-600 hover:border-purple-500"
              >
                {question}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Input */}
      <div className="p-4 border-t border-slate-700">
        <div className="flex gap-2">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSend();
              }
            }}
            placeholder="Ask about disease trends, correlations, or comparisons..."
            className="flex-1 resize-none h-20 bg-slate-800/50 text-slate-200 px-4 py-3 rounded-lg border border-slate-700 focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20 outline-none text-sm transition-all placeholder:text-slate-500"
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || isLoading}
            className="self-end bg-purple-600 hover:bg-purple-700 text-white p-3 rounded-lg transition-colors shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
        <p className="text-xs text-slate-500 mt-2">
          These insights are hypotheses only—not medical advice.
        </p>
      </div>
    </div>
  );
}