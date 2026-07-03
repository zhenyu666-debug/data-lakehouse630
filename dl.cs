using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Net;
using System.Threading;

class RailDownload
{
    static string outDir = @"C:\Users\Hasee\.qclaw\workspace\get_jobs\data-lakehouse\duckdb_railway";
    static int doneCount = 0;
    static int totalFiles = 7;
    static long totalBytes = 0;
    static long startTime;
    static long expectedTotal = 2508204800L;

    class FileEntry
    {
        public string name;
        public string url;
        public long expected;
        public FileEntry(string n, string u, long e)
        {
            name = n; url = u; expected = e;
        }
    }

    static FileEntry[] MakeFiles()
    {
        FileEntry[] arr = new FileEntry[7];
        arr[0] = new FileEntry("services-2019.csv.gz", "https://blobs.duckdb.org/nl-railway/services-2019.csv.gz", 348000000L);
        arr[1] = new FileEntry("services-2020.csv.gz", "https://blobs.duckdb.org/nl-railway/services-2020.csv.gz", 355000000L);
        arr[2] = new FileEntry("services-2021.csv.gz", "https://blobs.duckdb.org/nl-railway/services-2021.csv.gz", 350000000L);
        arr[3] = new FileEntry("services-2022.csv.gz", "https://blobs.duckdb.org/nl-railway/services-2022.csv.gz", 356000000L);
        arr[4] = new FileEntry("services-2023.csv.gz", "https://blobs.duckdb.org/nl-railway/services-2023.csv.gz", 346000000L);
        arr[5] = new FileEntry("services-2024.csv.gz", "https://blobs.duckdb.org/nl-railway/services-2024.csv.gz", 357000000L);
        arr[6] = new FileEntry("services-2025.csv.gz", "https://blobs.duckdb.org/nl-railway/services-2025.csv.gz", 396000000L);
        return arr;
    }

    static void Main()
    {
        startTime = Stopwatch.GetTimestamp();
        Directory.CreateDirectory(outDir);
        FileEntry[] files = MakeFiles();
        Console.WriteLine("Target: " + outDir);
        Console.WriteLine("Expected: " + (expectedTotal / 1e9).ToString("0.00") + " GB");
        Console.WriteLine(new string('=', 64));

        foreach (FileEntry f in files)
        {
            string path = Path.Combine(outDir, f.name);
            if (File.Exists(path))
            {
                long sz = new FileInfo(path).Length;
                if (sz > f.expected * 80 / 100)
                {
                    Interlocked.Add(ref totalBytes, sz);
                    Interlocked.Increment(ref doneCount);
                    Console.WriteLine("SKIP " + f.name + " (" + (sz / 1000000).ToString("0") + "MB)");
                }
            }
        }

        Console.WriteLine("Need to download: " + (totalFiles - doneCount) + " files\n");

        List<Thread> threads = new List<Thread>();
        foreach (FileEntry f in files)
        {
            string path = Path.Combine(outDir, f.name);
            if (!File.Exists(path) || new FileInfo(path).Length < f.expected * 80 / 100)
            {
                Thread t = new Thread(DownloadOne);
                t.Start(f);
                threads.Add(t);
                Thread.Sleep(300);
            }
        }

        foreach (Thread t in threads)
        {
            t.Join();
        }

        double elapsedSec = (Stopwatch.GetTimestamp() - startTime) / (double)Stopwatch.Frequency;
        Console.WriteLine("\n" + new string('=', 64));
        Console.WriteLine("ALL DONE in " + (elapsedSec / 60).ToString("0.0") + " min");
        long finalTotal = 0;
        int fileCount = 0;
        foreach (FileEntry f in files)
        {
            string path = Path.Combine(outDir, f.name);
            if (File.Exists(path))
            {
                finalTotal += new FileInfo(path).Length;
                fileCount++;
            }
        }
        Console.WriteLine("Files: " + fileCount + "/" + totalFiles
            + "  Total: " + (finalTotal / 1e9).ToString("0.00") + " GB");
    }

    static void DownloadOne(object obj)
    {
        FileEntry f = (FileEntry)obj;
        string path = Path.Combine(outDir, f.name);
        Console.WriteLine("DOWN " + f.name + " ...");
        Stopwatch sw = Stopwatch.StartNew();
        try
        {
            using (WebClient wc = new WebClient())
            {
                byte[] bytes = wc.DownloadData(f.url);
                File.WriteAllBytes(path, bytes);
                long sz = bytes.Length;
                Interlocked.Add(ref totalBytes, sz);
                int done = Interlocked.Increment(ref doneCount);
                double elapsed = (Stopwatch.GetTimestamp() - startTime) / (double)Stopwatch.Frequency;
                double avgMBs = totalBytes / 1e6 / elapsed;
                double etaMin = (expectedTotal - totalBytes) / (totalBytes / elapsed) / 60.0;
                if (etaMin < 0) etaMin = 0;
                Console.WriteLine("OK   [" + done + "/" + totalFiles + "] " + f.name
                    + "  " + (sz / 1000000).ToString("0") + "MB"
                    + "  avg=" + avgMBs.ToString("0") + "MB/s"
                    + "  eta=" + etaMin.ToString("0.0") + "min");
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine("FAIL " + f.name + ": " + ex.Message);
        }
    }
}
