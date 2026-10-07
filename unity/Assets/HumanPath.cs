using UnityEngine;

public class PedestrianCrosser : MonoBehaviour
{
    public Transform startPoint;
    public Transform endPoint;
    public float speed = 1.4f; // average human walking speed, m/s

    [Header("Randomization")]
    public float startOffsetVariance = 0.5f; // how many meters to randomly shift the start position
    public float speedVariance = 0.3f;       // how much the walking speed can randomly vary

    private Animator animator;
    private float t = 0f;
    private Vector3 actualStartPos;
    private float actualSpeed;

    void Start()
    {
        animator = GetComponent<Animator>();

        // Take the original startPoint position, then randomly shift it sideways
        Vector3 randomOffset = new Vector3(
            Random.Range(-startOffsetVariance, startOffsetVariance), 
            0f, 
            Random.Range(-startOffsetVariance, startOffsetVariance)
        );
        actualStartPos = startPoint.position + randomOffset;

        // Take the base speed, then randomly vary it a bit
        actualSpeed = speed + Random.Range(-speedVariance, speedVariance);

        transform.position = actualStartPos;
    }

    void Update()
    {
        t += (actualSpeed * Time.deltaTime) / Vector3.Distance(actualStartPos, endPoint.position);
        transform.position = Vector3.Lerp(actualStartPos, endPoint.position, t);
        transform.LookAt(endPoint.position);

        if (t >= 1f)
        {
            enabled = false; // stop at destination
        }
    }
}