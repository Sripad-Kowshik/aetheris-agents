if System.get_env("BANK_STATEMENT_MCP_ENABLED") == "true" do
  url = System.get_env("BANK_STATEMENT_MCP_URL") || ""
  uri = URI.parse(url)

  unless uri.scheme in ["http", "https"] && is_binary(uri.host) && uri.host != "" &&
           is_nil(uri.userinfo) && is_nil(uri.fragment) do
    raise "BANK_STATEMENT_MCP_URL must be an HTTP(S) MCP endpoint without credentials or a fragment"
  end

  unless uri.scheme == "https" || uri.host in ["localhost", "127.0.0.1", "::1"] do
    raise "BANK_STATEMENT_MCP_URL must use HTTPS except on loopback"
  end

  timeout_ms =
    case Integer.parse(System.get_env("BANK_STATEMENT_MCP_TIMEOUT_MS", "30000")) do
      {value, ""} when value > 0 -> value
      _ -> raise "BANK_STATEMENT_MCP_TIMEOUT_MS must be a positive integer"
    end

  headers =
    System.get_env()
    |> Enum.filter(fn {key, _} -> String.starts_with?(key, "BANK_STATEMENT_MCP_HEADER_") end)
    |> Map.new(fn {key, value} ->
      name =
        key
        |> String.replace_prefix("BANK_STATEMENT_MCP_HEADER_", "")
        |> String.downcase()
        |> String.replace("_", "-")

      invalid_value? =
        String.trim(value) == "" ||
          Enum.any?(String.to_charlist(value), fn char ->
            (char < 0x20 and char != 0x09) or char == 0x7F
          end)

      unless Regex.match?(~r/^[a-z0-9][a-z0-9-]*$/, name) && !invalid_value? do
        raise "Invalid Bank Statement MCP header: #{key}"
      end

      {name, value}
    end)

  %{
    server_id: "bank_statement",
    transport: :http,
    url: url,
    headers: headers,
    timeout_ms: timeout_ms
  }
end
