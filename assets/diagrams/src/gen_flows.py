import html
from pathlib import Path

OUT = Path(__file__).resolve().parent


def label(title, lines):
    parts = [f"<b>{html.escape(title, quote=False)}</b>"]
    for instr, comment in lines:
        if instr:
            parts.append(f"<code>{html.escape(instr, quote=False)}</code>")
        parts.append(f"// {html.escape(comment, quote=False)}")
    return "<br/>".join(parts)


DIAGRAMS = {
    "service-entry-flow": {
        "nodes": {
            "A": ("block", "First setup and IPC creation", [
                ("004845DD  call sub_4511E0", "Calls the first setup helper; EAX receives its status."),
                ("004845E2  mov ecx, eax", "Moves the status into ECX as the this pointer for the next call."),
                ("004845E4  call sub_452470", "Creates the named mutex and IPC sections before SCM registration."),
                ("004845E9  test eax, eax", "Tests the setup result for zero."),
                ("004845EB  je loc_48498D", "Jumps to the failure path when setup returns zero."),
            ]),
            "B": ("block", "Second setup path", [
                ("004845F1  call sub_451240", "Calls the second initialization helper."),
                ("004845F6  mov ecx, eax", "Passes its result to the next setup call in ECX."),
                ("004845F8  call sub_452B20", "Runs the second setup path and creates more engine state."),
                ("004845FD  test eax, eax", "Checks the second setup result for zero."),
                ("004845FF  je loc_48498D", "Jumps to the same failure path on zero."),
            ]),
            "C": ("block", "SCM dispatch table", [
                ("00484605  lea eax, [esp+0x20]", "Computes the address of the SCM service table on the stack."),
                ("00484609  mov dword ptr [esp+0x20], 0x82B3C4", "Stores the HTTPDebuggerPro service name pointer."),
                ("00484611  push eax", "Pushes the service table pointer for the SCM call."),
                ("00484612  mov dword ptr [esp+0x28], 0x484440", "Stores the ServiceMain pointer at 0x484440."),
                ("0048462A  call dword ptr [0x74F074]", "Calls StartServiceCtrlDispatcherA to hand control to the SCM."),
            ]),
            "FAIL": ("fail", "loc_48498D", [(None, "Failure or cleanup path outside this excerpt.")]),
            "SCM": ("endnode", "SCM dispatch", [(None, "Calls ServiceMain at 0x484440.")]),
        },
        "edges": [
            ("A", "B", "nonzero", "solid"),
            ("A", "FAIL", "zero", "solid"),
            ("B", "C", "nonzero", "solid"),
            ("B", "FAIL", "zero", "solid"),
            ("C", "SCM", None, "solid"),
        ],
    },
    "service-ipc-flow": {
        "nodes": {
            "A": ("block", "Create the UI mutex", [
                ("004524D2  push 0x829270", "Pushes the Global\\HttpDebuggerUiStarted name."),
                ("004524D7  push 0", "Sets the initial owner to false."),
                ("004524D9  push [ebp-0xAC]", "Pushes the security attributes pointer."),
                ("004524E2  call dword ptr [0x74F1D8]", "Calls CreateMutexA to create the UI-present mutex."),
                ("004524E8  mov [esi+0x0C], eax", "Stores the mutex handle in the service object."),
                ("004524EB  test eax, eax", "Checks whether creation succeeded."),
                ("004524ED  je loc_45295B", "Branches to the failure path on a null handle."),
            ]),
            "B": ("block", "Create the Settings channel", [
                ("004524F3  push 0x1E", "Pushes the maximum name length."),
                ("004524F5  push 0x829290", "Pushes the Global\\HttpDebuggerIpcSettings name."),
                (None, "Intermediate argument setup omitted from this excerpt."),
                ("00452538  push ebx", "Pushes the channel flags."),
                ("00452539  push ecx", "Pushes the security attributes."),
                ("0045253A  push eax", "Pushes the object name."),
                ("0045253B  lea ecx, [esi+0x20]", "Points ECX at the Settings channel object."),
                ("0045253E  call sub_453B90", "Creates the Settings section channel."),
            ]),
            "C": ("block", "Create the command and transaction channels", [
                ("004525A6  push 0x8292D8", "Pushes the Global\\HttpDebuggerIpcEngineCommand name."),
                (None, "Command channel setup omitted from this excerpt."),
                ("0045268A  push 0x82934C", "Pushes the Global\\HttpDebuggerIpcHttpTransaction name."),
                ("004526C1  push 0x80", "Sets the transaction ring capacity to 128 slots."),
                ("004526C8  lea ecx, [esi+0x480]", "Points ECX at the transaction channel object."),
                ("004526CE  call sub_453B90", "Creates the transaction channel."),
            ]),
            "FAIL": ("fail", "loc_45295B", [(None, "Failure path outside this excerpt.")]),
            "READY": ("endnode", "IPC surface ready", [(None, "Six named channels plus the UI mutex.")]),
        },
        "edges": [
            ("A", "B", "success", "solid"),
            ("A", "FAIL", "failure", "solid"),
            ("B", "C", None, "solid"),
            ("C", "READY", None, "solid"),
        ],
    },
    "channel-map-flow": {
        "nodes": {
            "A": ("block", "Create the named section", [
                ("00454103  push 0", "Sets the high-order size to zero."),
                ("00454105  push 4", "Requests PAGE_READWRITE protection."),
                ("00454107  push [ebp-0x58]", "Pushes the channel security attributes."),
                ("0045410E  push -1", "Uses INVALID_HANDLE_VALUE for a paging-file-backed section."),
                ("00454110  call CreateFileMappingA", "Creates the named section."),
            ]),
            "B": ("block", "Map the section read/write", [
                (None, "Handle validation and name setup omitted from this excerpt."),
                ("00454133  push 0xF001F", "Requests FILE_MAP_ALL_ACCESS."),
                ("00454138  push esi", "Pushes the section handle."),
                ("00454139  call MapViewOfFile", "Maps the section into the service process."),
            ]),
            "READY": ("endnode", "Shared section", [(None, "The peer opens and maps the same name.")]),
        },
        "edges": [
            ("A", "B", None, "solid"),
            ("B", "READY", None, "solid"),
        ],
    },
    "ui-attach-flow": {
        "nodes": {
            "A": ("block", "Open the UI mutex", [
                ("004167F0  push 0xADEC30", "Pushes the Global\\HttpDebuggerUiStarted name."),
                ("004167F5  push 0", "Sets the inherit flag to false."),
                ("004167F7  push 0x1F0001", "Requests MUTEX_ALL_ACCESS."),
                ("004167FF  call OpenMutexA", "Opens the service-created UI mutex."),
                ("00416805  mov [esi+0x0C], eax", "Stores the mutex handle in the UI object."),
                ("00416808  test eax, eax", "Checks whether the open succeeded."),
                ("0041680A  je loc_416D01", "Branches to the failure path on a null handle."),
            ]),
            "B": ("block", "Open the channel names", [
                ("00416812  push 0xADEC50", "Pushes the Global\\HttpDebuggerIpcSettings name."),
                (None, "Mapping setup for this channel omitted."),
                ("0041685D  push 0xADEC98", "Pushes the Global\\HttpDebuggerIpcEngineCommand name."),
                (None, "Mapping setup for this channel omitted."),
                ("004168AD  push 0xADECBC", "Pushes the Global\\HttpDebuggerIpcHttpNotification name."),
                (None, "Mapping setup for this channel omitted."),
                ("004168F8  push 0xADECE4", "Pushes the Global\\HttpDebuggerIpcConnectionInfo name."),
                (None, "Mapping setup for this channel omitted."),
                ("0041693F  push 0xADED0C", "Pushes the Global\\HttpDebuggerIpcHttpTransaction name."),
            ]),
            "C": ("helper", "sub_417A90", [(None, "Maps each named channel in turn.")]),
            "FAIL": ("fail", "loc_416D01", [(None, "Failure path outside this excerpt.")]),
            "READY": ("endnode", "UI attached", [(None, "Same sections as the service, different process.")]),
        },
        "edges": [
            ("A", "B", "success", "solid"),
            ("A", "FAIL", "failure", "solid"),
            ("B", "C", "each name", "solid"),
            ("C", "READY", None, "solid"),
        ],
    },
    "ui-map-flow": {
        "nodes": {
            "A": ("block", "Create the named section", [
                ("00417E77  push 0", "Sets the high-order size to zero."),
                ("00417E79  push 4", "Requests PAGE_READWRITE protection."),
                ("00417E7B  push [ebp-0x54]", "Pushes the channel security attributes."),
                ("00417E82  push -1", "Uses INVALID_HANDLE_VALUE for a paging-file-backed section."),
                ("00417E84  call CreateFileMappingA", "Creates the named section."),
            ]),
            "B": ("block", "Map the section read/write", [
                (None, "Handle validation and name setup omitted from this excerpt."),
                ("00417EA7  push 0xF001F", "Requests FILE_MAP_ALL_ACCESS."),
                ("00417EAD  call MapViewOfFile", "Maps the section into the UI process."),
            ]),
            "READY": ("endnode", "Shared section", [(None, "The service opens and maps the same name.")]),
        },
        "edges": [
            ("A", "B", None, "solid"),
            ("B", "READY", None, "solid"),
        ],
    },
    "ca-import-flow": {
        "nodes": {
            "A": ("block", "Select the store scope", [
                ("004DA9AD  cmp [ebp+0x14], 0", "Compares the caller's scope argument with zero."),
                ("004DA9B1  jne 0x4DA9C1", "Branches to the other scope path when it is nonzero."),
                ("004DA9B3  mov [ebp-0x58], 0x20", "Sets the provider flags to 0x20."),
                ("004DA9BA  mov [ebp-0x50], 0x20000", "Selects CERT_SYSTEM_STORE_LOCAL_MACHINE."),
            ]),
            "B": ("block", "Open LocalMachine Root", [
                ("004DA9E8  lea eax, [ebp-0x44]", "Loads the address of the converted Root store name."),
                ("004DA9EB  push eax", "Pushes the store name."),
                ("004DA9EC  mov ecx, [ebp-0x50]", "Reloads the LocalMachine scope flags."),
                ("004DA9EF  push ecx", "Pushes the scope flags."),
                ("004DA9F0  push 0", "Passes a null provider parameter."),
                ("004DA9F2  push 0x10001", "Selects X509 and PKCS_7 ASN encodings."),
                ("004DA9F7  push 0xA", "Selects CERT_STORE_PROV_SYSTEM_W."),
                ("004DA9F9  call CertOpenStore", "Opens the LocalMachine Root store."),
            ]),
            "C": ("block", "Add the encoded certificate", [
                ("004DAA0A  lea edx, [ebp-0x4C]", "Computes the output cert-context slot."),
                ("004DAA0D  push edx", "Pushes the cert-context output pointer."),
                ("004DAA0E  push 2", "Uses CERT_STORE_ADD_USE_EXISTING."),
                ("004DAA10  mov eax, [ebp+0xC]", "Loads the certificate length."),
                ("004DAA13  push eax", "Pushes the certificate length."),
                ("004DAA14  mov ecx, [ebp+8]", "Loads the certificate byte pointer."),
                ("004DAA17  push ecx", "Pushes the certificate bytes."),
                ("004DAA18  push 1", "Selects X509_ASN_ENCODING."),
                ("004DAA1A  mov edx, [ebp-0x48]", "Loads the open store handle."),
                ("004DAA1D  push edx", "Pushes the store handle."),
                ("004DAA1E  call CertAddEncodedCertificateToStore", "Adds the CA to the machine Root store."),
            ]),
            "OTHER": ("fail", "Other store scope", [(None, "Outside this excerpt.")]),
            "TRUST": ("endnode", "Machine trust anchor", [(None, "Persists after service removal.")]),
        },
        "edges": [
            ("A", "B", "zero", "solid"),
            ("A", "OTHER", "nonzero", "solid"),
            ("B", "C", None, "solid"),
            ("C", "TRUST", None, "solid"),
        ],
    },
}


def generate(name, spec):
    lines = ["flowchart TB"]
    for node_id, (kind, title, body) in spec["nodes"].items():
        lines.append(f'  {node_id}["{label(title, body)}"]')
    lines.append("")
    for src, dst, edge_label, style in spec["edges"]:
        if style == "dotted":
            arrow = "-.->"
        else:
            arrow = "-->"
        if edge_label:
            lines.append(f"  {src} {arrow}|{edge_label}| {dst}")
        else:
            lines.append(f"  {src} {arrow} {dst}")
    lines.append("")
    lines.append("  classDef block fill:#ffffff,stroke:#111111,color:#111111,stroke-width:1.5px;")
    lines.append("  classDef helper fill:#f4f4f4,stroke:#111111,color:#111111,stroke-width:1.5px,stroke-dasharray:4 2;")
    lines.append("  classDef fail fill:#ffffff,stroke:#111111,color:#111111,stroke-width:1.5px,stroke-dasharray:2 2;")
    lines.append("  classDef endnode fill:#111111,stroke:#111111,color:#ffffff,stroke-width:1.5px;")
    for node_id, (kind, _, _) in spec["nodes"].items():
        lines.append(f"  class {node_id} {kind};")
    lines.append("  linkStyle default stroke:#111111,stroke-width:1.5px;")
    (OUT / f"{name}.mmd").write_text("\n".join(lines) + "\n")


for name, spec in DIAGRAMS.items():
    generate(name, spec)

print("wrote", ", ".join(f"{name}.mmd" for name in DIAGRAMS))
