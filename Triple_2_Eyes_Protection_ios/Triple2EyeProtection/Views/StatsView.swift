import SwiftUI
import Charts

/// Usage statistics view with a bar chart of daily rest counts
/// and the summary table from UsageStore. This is the "usage curve" feature
/// the Android version still lacks.
struct StatsView: View {
    @State private var dailyData: [(date: Date, count: Int)] = []

    var body: some View {
        List {
            // Chart section
            Section("休息曲线（近30天）") {
                Chart(dailyData, id: \.date) { item in
                    BarMark(
                        x: .value("日期", item.date, unit: .day),
                        y: .value("次数", item.count)
                    )
                    .foregroundStyle(AppTheme.primary.gradient)
                }
                .frame(height: 200)
                .chartXAxis {
                    AxisMarks(values: .stride(by: .day, count: 5)) { _ in
                        AxisValueLabel(format: .dateTime.month().day())
                    }
                }
            }

            // Summary table
            Section("统计摘要") {
                ForEach(summaryLines, id: \.self) { line in
                    Text(line)
                        .font(.subheadline)
                }
            }
        }
        .navigationTitle("休息统计")
        .onAppear {
            dailyData = UsageStore.shared.dailyRestCounts(days: 30)
        }
    }

    private var summaryLines: [String] {
        UsageStore.shared.summary().split(separator: "\n").map(String.init)
    }
}
