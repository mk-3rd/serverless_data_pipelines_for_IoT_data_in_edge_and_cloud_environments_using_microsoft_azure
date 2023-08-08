import csv
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt


def convert_to_csv(text_file):
    counter = 30
    with open('edge_log.csv', 'w', newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',')
        writer.writerow(['compression_start', 'compression_end', 'upload_start', 'upload_end', "compression_duration",
                         "upload_duration"])

        with open(text_file, 'r') as source_file:
            next_row = []
            row_count = 0
            for line in source_file:
                if row_count == 0 and "COMPRESSION START:" in line:
                    next_row.append(line[19:].strip())
                    row_count += 1
                elif row_count == 1:
                    next_row.append(line[17:].strip())
                    row_count += 1
                elif row_count == 2:
                    next_row.append(line[14:].strip())
                    row_count += 1
                elif row_count == 3:
                    next_row.append(line[18:].strip())
                    start_compression = datetime.strptime(next_row[0], '%Y-%m-%d %H:%M:%S.%f')
                    finish_compression = datetime.strptime(next_row[1], '%Y-%m-%d %H:%M:%S.%f')
                    start_upload = datetime.strptime(next_row[2], '%Y-%m-%d %H:%M:%S.%f')
                    finish_upload = datetime.strptime(next_row[3], '%Y-%m-%d %H:%M:%S.%f')
                    compression_time = round(((finish_compression - start_compression).total_seconds() * 1000), 3)
                    upload_time = round(((finish_upload - start_upload).total_seconds() * 1000), 3)
                    next_row.append(compression_time)
                    next_row.append(upload_time)
                    writer.writerow(next_row)
                    next_row = []
                    row_count = 0


def reverse_csv_rows(input_file, output_file, experiment_start_row):
    with open(input_file, 'r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        rows = list(reader)
        header = rows[0]
        header[0] = "timestamp [UTC]"
        data = rows[1:]

    reversed_data = data[::-1]
    reversed_data = reversed_data[experiment_start_row:]  # remove some unneeded rows before experiment started

    with open(output_file, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(header)
        writer.writerows(reversed_data)


def filter_successful_rows(input_file, output_file):
    filtered_rows = []

    with open(input_file, 'r') as file:
        reader = csv.reader(file)
        header = next(reader)  # Read the header row
        filtered_rows.append(header)

        for row in reader:
            if row[header.index('success')] == 'True':
                filtered_rows.append(row)

    with open(output_file, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(filtered_rows)


def remove_unneeded_rows(input_file, output_file, row_numbers_to_remove):
    rows_to_keep = []

    with open(input_file, 'r') as file:
        reader = csv.reader(file)
        for row_number, row in enumerate(reader, start=1):
            if row_number not in row_numbers_to_remove:
                rows_to_keep.append(row)

    with open(output_file, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(rows_to_keep)


def combine_csv_files(input_files, output_file, types):
    combined_rows = []
    for input_file in range(len(input_files)):
        with open(input_files[input_file], 'r') as file:
            reader = csv.reader(file)
            rows = list(reader)
            if input_file == 0:
                combined_rows = rows
            else:
                for row in range(len(rows)):
                    if row == 0:
                        for column in range(len(rows[0])):
                            rows[0][column] = types[input_file] + "-" + rows[0][column]

                    combined_row = combined_rows[row] + rows[row]
                    combined_rows[row] = combined_row

    with open(output_file, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(combined_rows)


def calculate_total_time(input_file, output_file):
    final_rows = []
    with open(input_file, 'r') as file:
        reader = csv.reader(file)
        rows = list(reader)
        header = (rows[0] + ["total-processing-time", "total-time"])
        final_rows.append(header)

        # total-time is upload start until aeneas start + aeneas duration + compression duration
        # total-processing is all processing times combined

        for row in rows[1:]:
            upload_start = datetime.strptime(row[header.index('upload_start')], "%Y-%m-%d %H:%M:%S.%f")
            aeneas_start = datetime.strptime(row[header.index('aeneas-timestamp [UTC]')], "%m/%d/%Y, %I:%M:%S.%f %p")
            compression_duration = row[header.index('compression_duration')]
            decompress_duration = row[header.index('decompress-duration')]
            aeneas_duration = row[header.index('aeneas-duration')]
            total_time = round(
                ((aeneas_start - upload_start).total_seconds() * 1000) + float(compression_duration) + float(
                    aeneas_duration), 3)
            total_processing_time = round(
                float(compression_duration) + float(decompress_duration) + float(aeneas_duration), 3)
            final_rows.append(row + [total_processing_time, total_time])

    with open(output_file, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(final_rows)


def get_plot_data(filename, column_name):
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        rows = list(reader)
        column_index = rows[0].index(column_name)
        rows.pop(0)
        data_list = []
        for row in rows:
            data_list.append(round(float(row[column_index])))
        out_data = [data_list[i:i + 10] for i in range(0, 110, 10)]
        out_data = out_data + [data_list[110:118]]
        out_data = out_data + [data_list[i:i + 10] for i in range(118, len(data_list), 10)]
        out_data = [out_data[i:i + 5] for i in range(0, len(out_data), 5)]

    return out_data


def get_aeneas_plot(data):
    columns = ["1s", "3s", "10s", "30s", "60s"]

    fig, axs = plt.subplots(3, 3)

    axs[0, 0].boxplot(data[0])
    axs[0, 0].set_title('Function plan 1 - 500KB')
    axs[0, 0].set_xticklabels(columns)
    axs[0, 0].set_ylabel("Duration in milliseconds")
    axs[0, 0].grid(visible=True, color="silver", linestyle=":")

    axs[1, 0].boxplot(data[1])
    axs[1, 0].set_title('Function plan 1 - 5MB')
    axs[1, 0].set_xticklabels(columns)
    axs[1, 0].set_ylabel("Duration in milliseconds")
    axs[1, 0].grid(visible=True, color="silver", linestyle=":")

    axs[2, 0].boxplot(data[2])
    axs[2, 0].set_title('Function plan 1 - 50MB')
    axs[2, 0].set_xticklabels(columns)
    axs[2, 0].set_ylabel("Duration in milliseconds")
    axs[2, 0].grid(visible=True, color="silver", linestyle=":")

    axs[0, 1].boxplot(data[3])
    axs[0, 1].set_title('Function plan 2 - 500KB')
    axs[0, 1].set_xticklabels(columns)
    axs[0, 1].grid(visible=True, color="silver", linestyle=":")

    axs[1, 1].boxplot(data[4])
    axs[1, 1].set_title('Function plan 2 - 5MB')
    axs[1, 1].set_xticklabels(columns)
    axs[1, 1].grid(visible=True, color="silver", linestyle=":")

    axs[2, 1].boxplot(data[5])
    axs[2, 1].set_title('Function plan 2 - 50MB')
    axs[2, 1].set_xticklabels(columns)
    axs[2, 1].grid(visible=True, color="silver", linestyle=":")

    axs[0, 2].boxplot(data[6])
    axs[0, 2].set_title('Function plan 3 - 500KB')
    axs[0, 2].set_xticklabels(columns)
    axs[0, 2].grid(visible=True, color="silver", linestyle=":")

    axs[1, 2].boxplot(data[7])
    axs[1, 2].set_title('Function plan 3 - 5MB')
    axs[1, 2].set_xticklabels(columns)
    axs[1, 2].grid(visible=True, color="silver", linestyle=":")

    axs[2, 2].boxplot(data[8])
    axs[2, 2].set_title('Function plan 3 - 50MB')
    axs[2, 2].set_xticklabels(columns)
    axs[2, 2].grid(visible=True, color="silver", linestyle=":")

    fig.subplots_adjust(left=0.068, right=0.98, bottom=0.033, top=0.982,
                        hspace=0.179, wspace=0.195)
    plt.show()


def generate_total_plot(data, name):
    plot_data = []
    final_data = []
    for i in range(0, len(data)):
        plot_data.append([])
        for j in range(0, len(data[i])):
            plot_data[i] = plot_data[i] + data[i][j]
    for z in range(0, len(plot_data)):
        final_data.append(round(sum(plot_data[z]) / len(plot_data[z])))

    standard_deviation = []
    for x in plot_data:
        standard_deviation.append(np.std(x, ddof=1))

    std_arranged = []
    for y in range(0, 3):
        new_list = [standard_deviation[y], standard_deviation[y + 3], standard_deviation[y + 6]]
        std_arranged.append(new_list)

    plans = ("Plan 1", "Plan 2", "Plan 3")
    time_means = {
        '500KB': (final_data[0], final_data[3], final_data[6]),
        '5MB': (final_data[1], final_data[4], final_data[7]),
        '50MB': (final_data[2], final_data[5], final_data[8]),
    }

    x = np.arange(len(plans))
    width = 0.25
    multiplier = 0
    fig, ax = plt.subplots(layout='constrained')

    for attribute, measurement in time_means.items():
        offset = width * multiplier
        rects = ax.bar(x + offset, measurement, width, label=attribute, yerr=std_arranged[multiplier], ecolor='red',
                       capsize=7, zorder=3)
        ax.bar_label(rects, padding=3)
        multiplier += 1

    ax.set_ylabel('Duration in milliseconds')
    ax.set_title(name)
    ax.set_xticks(x + width, plans)
    ax.legend(loc='upper right', ncols=3)
    ax.grid(visible=True, color="silver", linestyle=":", zorder=1)

    plt.show()


def generate_total_plot_box(data1, data2):
    configured_process = []
    configured_end_to_end = []

    configured_process_structured = []
    configured_end_to_end_structured = []

    for row in range(0, len(data1)):
        configured_process.append(data1[row][0] + data1[row][1] + data1[row][2] + data1[row][3] + data1[row][4])

    for row in range(0, len(data2)):
        configured_end_to_end.append(data2[row][0] + data2[row][1] + data2[row][2] + data2[row][3] + data2[row][4])

    for y in range(0, 9, 3):
        new_list = [configured_process[y], configured_process[y + 1], configured_process[y + 2]]
        configured_process_structured.append(new_list)

    for y in range(0, 9, 3):
        new_list = [configured_end_to_end[y], configured_end_to_end[y + 1], configured_end_to_end[y + 2]]
        configured_end_to_end_structured.append(new_list)

    columns = ["500KB", "5MB", "50MB"]

    fig, axs = plt.subplots(2, 3)

    axs[0, 0].boxplot(configured_process_structured[0])
    axs[0, 0].set_title('All processing - Plan 1')
    axs[0, 0].set_xticklabels(columns)
    axs[0, 0].set_ylabel("Duration in milliseconds")
    axs[0, 0].grid(visible=True, color="silver", linestyle=":")

    axs[0, 1].boxplot(configured_process_structured[1])
    axs[0, 1].set_title('All processing - Plan 2')
    axs[0, 1].set_xticklabels(columns)
    axs[0, 1].grid(visible=True, color="silver", linestyle=":")

    axs[0, 2].boxplot(configured_process_structured[2])
    axs[0, 2].set_title('All processing - Plan 3')
    axs[0, 2].set_xticklabels(columns)
    axs[0, 2].grid(visible=True, color="silver", linestyle=":")

    axs[1, 0].boxplot(configured_end_to_end_structured[0])
    axs[1, 0].set_title('End to end flow - Plan 1')
    axs[1, 0].set_xticklabels(columns)
    axs[1, 0].set_ylabel("Duration in milliseconds")
    axs[1, 0].grid(visible=True, color="silver", linestyle=":")

    axs[1, 1].boxplot(configured_end_to_end_structured[1])
    axs[1, 1].set_title('End to end flow - Plan 2')
    axs[1, 1].set_xticklabels(columns)
    axs[1, 1].grid(visible=True, color="silver", linestyle=":")

    axs[1, 2].boxplot(configured_end_to_end_structured[2])
    axs[1, 2].set_title('End to end flow - Plan 3')
    axs[1, 2].set_xticklabels(columns)
    axs[1, 2].grid(visible=True, color="silver", linestyle=":")

    fig.subplots_adjust(left=0.068, right=0.98, bottom=0.033, top=0.982,
                        hspace=0.179, wspace=0.195)
    plt.show()


if __name__ == '__main__':
    # Create single .csv file that contains all experiment information
    convert_to_csv("edge_log.txt")
    reverse_csv_rows("decompress-all.csv", "decompress-all-reversed.csv", 131)
    filter_successful_rows("decompress-all-reversed.csv", "decompress-all-filtered.csv")
    remove_unneeded_rows("decompress-all-filtered.csv", "decompress-all-clean.csv",
                         [52, 53, 104, 105, 154, 155, 156, 307, 308])
    remove_unneeded_rows("edge_log.csv", "edge-log-clean.csv",
                         [114, 116])
    reverse_csv_rows("aeneas-all.csv", "aeneas-all-reversed.csv", 7)
    filter_successful_rows("aeneas-all-reversed.csv", "aeneas-all-filtered.csv")
    remove_unneeded_rows("aeneas-all-filtered.csv", "aeneas-all-clean.csv",
                         [52, 53, 104, 105, 154, 155, 156, 307, 308])
    combine_csv_files(["edge-log-clean.csv", "decompress-all-clean.csv", "aeneas-all-clean.csv"], "pipeline.csv",
                      ["edge", "decompress", "aeneas"])
    calculate_total_time("pipeline.csv", "pipeline-final.csv")

    # Create plots for thesis paper
    aeneas_data = get_plot_data("pipeline-final.csv", "aeneas-duration")
    get_aeneas_plot(aeneas_data)

    total_processing_data = get_plot_data("pipeline-final.csv", "total-processing-time")
    generate_total_plot(total_processing_data, 'Pipeline total processing duration')

    total_end_to_end_data = get_plot_data("pipeline-final.csv", "total-time")
    generate_total_plot(total_end_to_end_data, 'Pipeline total end to end duration')

    generate_total_plot_box(get_plot_data("pipeline-final.csv", "total-processing-time"),
                            get_plot_data("pipeline-final.csv", "total-time"))
