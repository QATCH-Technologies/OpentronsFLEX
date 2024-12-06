from flask import Flask, request, jsonify

app = Flask(__name__)

# Mock database to store run data and commands
runs = {}
commands = {}
robot_state = {"home": False, "pipette_loaded": False}


@app.route("/runs", methods=["POST"])
def create_run():
    run_id = f"run_{len(runs) + 1}"
    runs[run_id] = {"id": run_id, "commands": ["cmd_1", "cmd_2", "cmd_3"]}
    print(runs)
    return jsonify({"data": {"id": run_id}}), 201


@app.route("/runs/<run_id>/commands", methods=["POST"])
def create_command(run_id):
    if run_id not in runs:
        return jsonify({"error": "Run ID not found"}), 404

    command = request.get_json()["data"]
    command_id = f"cmd_{len(commands) + 1}"
    command_result = {}

    # Handle different command types
    if command["commandType"] == "loadLabware":
        labware_id = f"labware_{len(commands) + 1}"
        command_result = {"labwareId": labware_id}

    elif command["commandType"] == "loadPipette":
        pipette_id = f"pipette_{len(commands) + 1}"
        robot_state["pipette_loaded"] = True
        command_result = {"pipetteId": pipette_id}

    elif command["commandType"] == "pickUpTip":
        if not robot_state["pipette_loaded"]:
            return jsonify({"error": "No pipette loaded"}), 400
        command_result = {"status": "tip picked up"}

    elif command["commandType"] == "aspirate":
        if not robot_state["pipette_loaded"]:
            return jsonify({"error": "No pipette loaded"}), 400
        command_result = {
            "status": f"aspirated {command['params']['volume']} µL"}

    elif command["commandType"] == "dispense":
        if not robot_state["pipette_loaded"]:
            return jsonify({"error": "No pipette loaded"}), 400
        command_result = {
            "status": f"dispensed {command['params']['volume']} µL"}

    elif command["commandType"] == "blowout":
        if not robot_state["pipette_loaded"]:
            return jsonify({"error": "No pipette loaded"}), 400
        command_result = {"status": "blowout completed"}

    elif command["commandType"] == "dropTip":
        if not robot_state["pipette_loaded"]:
            return jsonify({"error": "No pipette loaded"}), 400
        command_result = {"status": "tip dropped"}

    # New command for moving to a well
    elif command["commandType"] == "moveToWell":
        labware_id = command["params"]["labwareId"]
        well_name = command["params"]["wellName"]
        pipette_id = command["params"]["pipetteId"]
        well_location = command["params"]["wellLocation"]

        # Simulate moving the pipette to the well (mock action)
        command_result = {
            "status": f"Moved to well {well_name} in labware {labware_id} with pipette {pipette_id}. "
                      f"Origin: {well_location['origin']}, Offset: {well_location['offset']}"
        }

    else:
        return jsonify({"error": f"Unknown command type: {command['commandType']}"}), 400

    # Store command and its result
    commands[command_id] = {
        "id": command_id,
        "commandType": command["commandType"],
        "result": command_result,
    }
    runs[run_id]["commands"].append(command_id)

    return jsonify({"data": {"id": command_id, "result": command_result}}), 201


@app.route("/robot/home", methods=["POST"])
def home_robot():
    robot_state["home"] = True
    return jsonify({"message": "Robot homed successfully"}), 200


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=31950)
