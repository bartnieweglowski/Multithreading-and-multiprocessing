import concurrent.futures
import time
import platform
import os
import sys

__author__ = 'Bartłomiej Niewęgłowski'

NUMBERS = [
    15972490, 80247910, 92031257, 75940266,
    97986012, 87599664, 75231321, 11138524,
    68870499, 11872796, 79132533, 40649382,
    63886074, 53146293, 36914087, 62770938
]


def compute(n):
    return sum(range(1, n + 1))


def benchmark_1_thread(numbers):
    ret = []
    start = time.perf_counter()
    for number in numbers:
        ret.append(compute(number))
    return time.perf_counter() - start


def benchmark_4_threads(numbers):
    start = time.perf_counter()
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        list(executor.map(compute, numbers))
    return time.perf_counter() - start


def benchmark_multiprocessed(numbers, max_workers):
    # If max_workers is None, ProcessPoolExecutor()
    #   will use as many processes (workers) as many are available on the CPU,
    #   as it is indicated in the documentation.
    start = time.perf_counter()
    with concurrent.futures.ProcessPoolExecutor(
            max_workers=max_workers) as executor:
        list(executor.map(compute, numbers))
    return time.perf_counter() - start


def benchmark(numbers=NUMBERS):
    print('Running 1-threaded benchmark...', end=' ')
    time_1_thread = benchmark_1_thread(numbers)

    print(
        f'DONE in {time_1_thread}s.\nRunning 4-threaded benchmark...',
        end=' '
    )
    time_4_threads = benchmark_4_threads(numbers)

    print(
        f'DONE in {time_4_threads}s.\nRunning 4 processes benchmark...',
        end=' '
    )
    mp_4 = benchmark_multiprocessed(numbers, max_workers=4)

    print(
        f'DONE in {mp_4}s.\nRunning CPU-based multiprocessed benchmark...',
        end=' '
    )
    mp_cpu = benchmark_multiprocessed(numbers, max_workers=None)

    print(f'DONE in {mp_cpu}s.')

    return [time_1_thread, time_4_threads, mp_4, mp_cpu]


def get_benchmark_results(numbers=NUMBERS):
    results = []
    for i in range(1, 6):
        print(f'Execution #{i}')
        results.append(benchmark(numbers))
    return results


def report_benchmarks_to_table(benchmarks):
    parts = []
    for i, results in enumerate(benchmarks, start=1):
        parts.append(
            '<tr><td>'
            + '</td><td>'.join(
                [str(i), *[f'{result:.3f}' for result in results]]
            )
            + '</td></tr>'
        )
    return ' \n '.join(parts)


def get_median(values):
    values = sorted(values)
    length = len(values)
    i = length // 2
    if length % 2 == 0:
        return sum(values[i:i + 2]) / 2
    return values[i]


def report_medians_to_table(benchmarks):
    medians = []
    for i in range(4):
        medians.append(
            f'{get_median([results[i] for results in benchmarks]):.3f}'
        )
    return (
        f'<tr><td>Medians:</td><td>' + '</td><td>'.join(medians) + '</td></tr>'
    )


def generate_report(benchmarks, output_filename='report.html'):
    doc = f"""<!DOCTYPE html>
    <html>
    <head>
    <meta charset="utf-8" />
    <title>Multithreading/Multiprocessing benchmark results</title>
    <style>

    body {{
      font-size: 10pt;
    }}

    h2 {{
      padding-top: 10pt;
    }}

    table {{
      font-family: arial, sans-serif;
      border-collapse: collapse;
      width: 100%;
      table-layout: fixed ;
    }}

    td, th {{
      border: 2px solid #b9b9b9;
      padding: 10px;
      text-align: center;
      width: 25% ;
    }}

    th {{
      background-color: #d5d5d5;
    }}

    td {{
    }}

    tr:nth-child(odd) {{
      background-color: #eeeeee;
    }}
    </style>
    </head>
    <body>

    <h1>Multithreading/Multiprocessing benchmark results</h1>
    <p>
    </p>

    <h2>Execution environment</h2>
    <p>
    Python version: {platform.python_version()}<br/>
    Interpreter: {platform.python_implementation()}<br/>
    Interpreter version: {sys.version}<br/>
    Operating system: {platform.system()}<br/>
    Operating system version: {platform.release()}<br/>
    Processor: {platform.processor()}<br/>
    CPUs: {os.cpu_count()}
    </p>

    <h2>Test results</h2>
    <p>The following table shows detailed test results:</p>
    <table>
      <tr>
        <th>Execution:</th>
        <th>1 thread (s)</th>
        <th>4 threads (s)</th>
        <th>4 processes (s)</th>
        <th>processes based on number of CPUs (s)</th>
      </tr>
      {report_benchmarks_to_table(benchmarks)}
    </table>

    <h2>Summary</h2>
    <p>The following table shows the median of all results:</p>
    <table>
      <tr>
        <th>Execution:</th>
        <th>1&nbsp;thread (s)</th>
        <th>4&nbsp;threads (s)</th>
        <th>4&nbsp;processes (s)</th>
        <th>processes based on number of CPUs (s)</th>
      </tr>
      {report_medians_to_table(benchmarks)}
    </table>

    <p>App author: {__author__}</p>

    </body>
    </html>
    """
    with open(output_filename, 'w', encoding='utf-8') as file:
        file.write(doc)
    print(f"The report has been saved to {output_filename}")


def main(numbers=NUMBERS):
    return generate_report(get_benchmark_results(numbers))


if __name__ == '__main__':
    main()
    