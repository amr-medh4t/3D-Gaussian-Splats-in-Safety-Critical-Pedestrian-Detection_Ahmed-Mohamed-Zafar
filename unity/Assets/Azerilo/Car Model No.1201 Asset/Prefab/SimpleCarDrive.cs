using UnityEngine;

public class SimpleCarDrive : MonoBehaviour
{
    public float speed = 15f;
    public float turnSpeed = 50f;

    private Rigidbody rb;

    void Start()
    {
        rb = GetComponent<Rigidbody>();
    }

    void FixedUpdate()
    {
        float forwardMove = Input.GetAxis("Vertical") * speed;
        float turnMove = Input.GetAxis("Horizontal") * turnSpeed;

        Vector3 movement = transform.forward * forwardMove * Time.fixedDeltaTime;
        rb.MovePosition(rb.position + movement);

        if (Mathf.Abs(forwardMove) > 0.01f)
        {
            Quaternion turnRotation = Quaternion.Euler(0f, turnMove * Time.fixedDeltaTime, 0f);
            rb.MoveRotation(rb.rotation * turnRotation);
        }
    }
}