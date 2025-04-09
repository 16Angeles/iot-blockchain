 for i in range(50): 
            temperature = round(25.0 + random.uniform(-2.0, 2.0), 2)
            payload = json.dumps({"temperature": temperature})
            client.publish(TOPIC, payload=payload, qos=1)
            print(f"[{i + 1}] Отправлено: {payload}")
            time.sleep(0.1) 
        client.disconnect()
