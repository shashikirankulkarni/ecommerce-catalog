package com.shashi.catalog.config;

/*
 * Guards against unresolved property placeholders.
 *
 * When Spring cannot resolve ${SOME_VAR} it does not fail - it leaves the
 * literal text "${SOME_VAR}" as the value. That is a non-blank string, so
 * @NotBlank is satisfied and the application starts holding nonsense,
 * failing much later at the first call that uses it.
 *
 * Called from the compact constructor of each @ConfigurationProperties
 * record, so the failure happens during binding, at startup, naming the
 * variable that is missing.
 */
final class ConfigGuard {

    private ConfigGuard() {
    }

    static void requireResolved(String property, String variable, String value) {
        if (value != null && value.startsWith("${")) {
            throw new IllegalStateException(
                    "Environment variable " + variable + " is not set, so " + property
                            + " resolved to the literal text " + value
                            + ". Set it in .env for local runs, or as an environment"
                            + " secret for a deployed environment.");
        }
    }
}
