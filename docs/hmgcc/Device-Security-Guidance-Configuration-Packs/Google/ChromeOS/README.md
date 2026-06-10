# ChromeOS Configuration Packs 2025
This archive contains important security policy settings which are recommended for a ChromeOS deployment. Other settings (e.g. server address, domain names) should be chosen according to the relevant network configuration. Where a configuration is not listed in this pack you should refer to the Google default option then decide on the setting based on your needs.

We recommend looking at the Google documentation on [Organisation Unit (OU) Management](https://support.google.com/a/answer/4352075?hl=en) before starting with these packs. Each organisation will have their preferred way of managing the organisational structure within Workspace and it may not fully align with all settings in this configuration pack.

The Configurations are split into 2 sections; User and Browser and Device.
`User and Browser` settings apply to the user accounts and any logins they make with the Chrome Browser for users in the OU these settings are applied to.
`Device` settings apply to devices which are in the OU these settings are applied to.

Remember, any guidance points given here are recommendations - they are not mandatory. Risk owners and administrators should agree a configuration which balances business requirements, usability and the security of the platform. 


## Additional Information
Below are areas of extra detail on some of the areas of the configuration set.

### Enrollment
By default you should prevent users from enrolling new devices into the organisation. 

Create an enrollment OU with enrollment users to allow new devices to be added to the organisation then moved to the relevant OU after initial enrollment. Enrollment OUs and Users shouldn't have additional permissions to access resources or administrative functions after login outside of their enrollment needs. This will prevent unauthorised devices from being automatically enrolled by an end user. 

By limiting the ability for user to enroll new devices and by forcing a user to enroll an un-enrolled device into workspace on first login you will be preventing users from accessing their workspace accounts on other non-enrolled/corporate machines.

### Ephemeral Mode (User data delete)
Within the Device Settings section of Workspace ChromeOS devices have the option to have User Data deleted on sign out (this setting also known as Ephemeral Mode). Ephemeral mode is great for a preventing a persistent presence on a device. An organisations standard users may find Ephemeral Mode cumbersome with the need to resync profile, settings and apps with internet connectivity required on every login. Organisations with administrative or higher privileged users could consider the use of ephemeral mode on devices such as PAW or other higher access machines to ensure no persistence exists between sessions. Ephemeral mode is also recommended for organisations using Kiosk and Guest modes.

When enabling Ephemeral mode, any settings for quick unlock with Pin or Fingerprint are unset and the user is only able to use password/hardware token authentication.

Full details on Ephemeral Mode can be found on the [Google Workspace Support pages](https://support.google.com/chrome/a/answer/3538894?hl=en).

### Extensions and Android Apps
Administrators should manage apps and extensions for ChromeOS users and devices via the Apps and Extensions settings. 

NCSC has published information within the [ChromeOS Device Security Guidance](https://www.ncsc.gov.uk/collection/device-security-guidance/platform-guides/chrome-os) page on its website to help administrators understand how Android Apps and Chrome Browser Extensions are handled on ChromeOS. 

## Google Workspace/Google Account Security
ChromeOS devices rely on the security policies that are implemented within your Workspace organisation which will strengthen the login process for your ChromeOS devices. Below are some configurations within Workspace which we would recommend you review as part of your ChromeOS deployment for your users Google Accounts. If using another Identity Provider (IdP) for your authentication (such as Microsoft Entra ID) then you will need to ensure that your security position on both IdPs secure your users appropriately.

### User Account Security Controls for Workspace
- `User accounts` - all accounts should have 2-Step Verification (2SV) enabled by default.
    - Under Security, Authentication, 2-step Verification` administrators should set policy based on their security profiles to balance security and usability of their 2SV. See NCSC Guidance on [Multi-factor Authentication](https://www.ncsc.gov.uk/collection/mfa-for-your-corporate-online-services).
    - After initial login to their ChromeOS devices, users should not need to complete 2SV again (subject to security posture rules users should assume they will need to 2SV but may not be presented. If the device is using Ephemeral Mode then the user will need 2SV on first login as it would class as first login every time)
    - If enrolling users in the Advanced Protection Program (APP, see below) then these policies will be overridden
- `Password Management` - Configure a strong password policy in line with company policy requirements. NCSC has recommended strategies for [Password administration for system owners](https://www.ncsc.gov.uk/collection/passwords)
- `Less Secure Apps` - This setting has now been deprecated by Google. Administrators should not re-enable or use apps that still have this dependency. For details on Less Secure Apps see this [Google Support Article](https://support.google.com/a/answer/6260879?hl=en) on the subject.
- `Advanced Protection Program (APP)` - Administrators should allow users to enroll in APP. Details on APP can be found on the [Google APP Website](https://landing.google.com/advancedprotection/)
    - APP overrides any 2SV policies you set
    - High Risk accounts or accounts with sensitive data stored should be enrolled
    - Users will need self-enroll with APP
- `Login Challenges` - Consider the use of [Login Challenges](https://support.google.com/a/answer/9022736) when Google detects suspicious attempts to access an account 

### App based Security Controls for Workspace
- `API Controls` - Administrators should deny any 3rd party app access unless explicitly allowed by the organisation. This list should be reviewed often.
- `Context Aware Access` - For online services using your Workspace account as the IdP consider the use of [Context-Aware Access](https://support.google.com/a/answer/9275380?hl=en)

### Workspace Alerting
Administrators should review all alerting within their Workspace account. By default Google enables certain rules which administrators should review and become familiar with. Once alerting has been reviewed a policy on how to manage and respond to alerts should be introduced based on the organisations risk needs. Consider adding additional alerts for extra protections or accesses (such as [Break Glass accounts](https://www.ncsc.gov.uk/blog-post/protecting-how-you-administer-cloud-services))

---
This configuration was last tested against ChromeOS 139.

Crown Copyright (c) 2025

