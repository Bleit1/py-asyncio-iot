import asyncio
import time
from iot.devices import HueLightDevice, SmartSpeakerDevice, SmartToiletDevice
from iot.message import Message, MessageType
from iot.service import IOTService, run_sequence, run_parallel


async def main() -> None:
    # create an IOT service
    service = IOTService()

    # create and register a few devices in parallel
    hue_light = HueLightDevice()
    speaker = SmartSpeakerDevice()
    toilet = SmartToiletDevice()

    hue_light_id, speaker_id, toilet_id = await asyncio.gather(
        service.register_device(hue_light),
        service.register_device(speaker),
        service.register_device(toilet),
    )

    # create a few programs
    wake_up_program = [
        Message(hue_light_id, MessageType.SWITCH_ON),
        Message(speaker_id, MessageType.SWITCH_ON),
        Message(speaker_id, MessageType.PLAY_SONG, "Rick Astley - Never Gonna Give You Up"),
    ]

    sleep_program = [
        Message(hue_light_id, MessageType.SWITCH_OFF),
        Message(speaker_id, MessageType.SWITCH_OFF),
        Message(toilet_id, MessageType.FLUSH),
        Message(toilet_id, MessageType.CLEAN),
    ]

    # Run the wake-up program: Lights & Speaker can turn on in parallel, but playing must wait
    await run_parallel(
        service.send_msg(wake_up_program[0]),  # Light ON
        service.send_msg(wake_up_program[1]),  # Speaker ON
    )
    await run_sequence(service.send_msg(wake_up_program[2]))  # Play song

    # Run the sleep program: Lights & Speaker can turn off in parallel, but Toilet must be sequential
    await run_parallel(
        service.send_msg(sleep_program[0]),  # Light OFF
        service.send_msg(sleep_program[1]),  # Speaker OFF
    )
    await run_sequence(
        service.send_msg(sleep_program[2]),  # Flush
        service.send_msg(sleep_program[3])   # Clean
    )

if __name__ == "__main__":
    start = time.perf_counter()
    asyncio.run(main())  # ✅ Use asyncio.run() to run the async function
    end = time.perf_counter()

    print("Elapsed:", end - start)