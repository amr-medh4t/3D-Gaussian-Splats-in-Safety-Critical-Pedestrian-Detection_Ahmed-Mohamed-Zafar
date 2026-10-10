using System;
using System.IO;
using UnityEngine;

public class TimeRecorder : MonoBehaviour
{
    [SerializeField] private float captureEverySeconds = 0.1f;
    [SerializeField] private string folderName = "TrainingDataset";

    private string folderPath;
    private int counter = 0;
    private float timer = 0f;
    private string sessionPrefix;

    void Start()
    {
        // Saves in the project root folder (outside Assets) so Unity never touches or purges it
        folderPath = Path.Combine(Directory.GetParent(Application.dataPath).FullName, folderName);

        if (!Directory.Exists(folderPath))
        {
            Directory.CreateDirectory(folderPath);
        }

        // Creates a unique prefix per play session: e.g. "run_20260915_143022"
        sessionPrefix = "run_" + DateTime.Now.ToString("yyyyMMdd_HHmmss");

        Debug.Log("Saving dataset to: " + folderPath);
    }

    void Update()
    {
        timer += Time.unscaledDeltaTime;

        if (timer >= captureEverySeconds)
        {
            string filename = Path.Combine(folderPath, $"{sessionPrefix}_frame_{counter:D05}.png");
            ScreenCapture.CaptureScreenshot(filename);
            counter++;
            timer = 0f;
        }
    }
}