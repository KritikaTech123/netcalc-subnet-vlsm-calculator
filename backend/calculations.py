"""IPv4 subnetting and VLSM calculations."""
from ipaddress import IPv4Network, IPv4Address, ip_network
from math import ceil, log2


def ip_class(address: IPv4Address) -> str:
    first = int(str(address).split(".")[0])
    if first < 128:
        return "A"
    if first < 192:
        return "B"
    if first < 224:
        return "C"
    if first < 240:
        return "D (Multicast)"
    return "E (Experimental)"


def usable_range(network: IPv4Network):
    hosts = list(network.hosts())
    if network.prefixlen == 32:
        return str(network.network_address), str(network.network_address)
    if network.prefixlen == 31:
        return str(network.network_address), str(network.broadcast_address)
    return str(hosts[0]), str(hosts[-1])


def subnet_calculation(address: str, prefix: int, mask: str | None = None) -> dict:
    if not 0 <= prefix <= 32:
        raise ValueError("CIDR prefix must be between 0 and 32.")
    if mask:
        try:
            mask_network = ip_network(f"0.0.0.0/{mask}")
        except ValueError as exc:
            raise ValueError("Subnet mask is invalid.") from exc
        if mask_network.prefixlen != prefix:
            raise ValueError("CIDR prefix and subnet mask do not match.")
    try:
        network = ip_network(f"{address}/{prefix}", strict=False)
    except ValueError as exc:
        raise ValueError("Enter a valid IPv4 address and CIDR prefix.") from exc
    first, last = usable_range(network)
    total = network.num_addresses
    usable = total if prefix >= 31 else max(total - 2, 0)
    address_obj = IPv4Address(address)
    host_bits = 32 - prefix
    wildcard = IPv4Address(int(IPv4Address("255.255.255.255")) ^ int(network.netmask))
    return {
        "ip_address": str(address_obj),
        "network_address": str(network.network_address),
        "subnet_mask": str(network.netmask),
        "cidr": f"/{prefix}",
        "broadcast_address": str(network.broadcast_address),
        "first_usable": first,
        "last_usable": last,
        "total_addresses": total,
        "usable_hosts": usable,
        "wildcard_mask": str(wildcard),
        "ip_class": ip_class(address_obj),
        "network_bits": prefix,
        "host_bits": host_bits,
    }


def vlsm_calculation(base: str, departments: list[dict]) -> dict:
    try:
        parent = ip_network(base, strict=False)
    except ValueError as exc:
        raise ValueError("Enter a valid base network such as 192.168.1.0/24.") from exc
    if parent.version != 4:
        raise ValueError("Only IPv4 networks are supported.")
    if not departments:
        raise ValueError("Add at least one department.")
    normalized = []
    for item in departments:
        name = str(item.get("name", "")).strip()
        try:
            hosts = int(item.get("hosts", 0))
        except (TypeError, ValueError) as exc:
            raise ValueError(f"Host count for {name or 'a department'} is invalid.") from exc
        if not name or hosts < 1:
            raise ValueError("Every department needs a name and at least one host.")
        required = hosts + 2
        bits = max(2, ceil(log2(required)))
        prefix = 32 - bits
        if prefix < parent.prefixlen:
            raise ValueError(f"{name} needs more addresses than the parent network provides.")
        normalized.append((name, hosts, prefix))
    normalized.sort(key=lambda row: row[1], reverse=True)
    cursor = int(parent.network_address)
    allocations = []
    for name, hosts, prefix in normalized:
        size = 2 ** (32 - prefix)
        cursor = ((cursor + size - 1) // size) * size
        candidate = IPv4Network((cursor, prefix))
        if not candidate.subnet_of(parent):
            raise ValueError("The requested departments exceed the parent network.")
        first, last = usable_range(candidate)
        allocations.append({
            "name": name, "required_hosts": hosts, "network": str(candidate.network_address),
            "cidr": f"/{prefix}", "subnet_mask": str(candidate.netmask),
            "broadcast": str(candidate.broadcast_address), "first_usable": first,
            "last_usable": last, "total_addresses": candidate.num_addresses,
            "usable_hosts": candidate.num_addresses if prefix >= 31 else candidate.num_addresses - 2,
        })
        cursor = int(candidate.broadcast_address) + 1
    used = sum(item["total_addresses"] for item in allocations)
    return {
        "parent_network": str(parent), "allocations": allocations,
        "total_addresses": parent.num_addresses, "allocated_addresses": used,
        "unused_addresses": parent.num_addresses - used,
        "unused_start": str(IPv4Address(cursor)) if cursor <= int(parent.broadcast_address) else None,
        "unused_end": str(parent.broadcast_address) if cursor <= int(parent.broadcast_address) else None,
    }
